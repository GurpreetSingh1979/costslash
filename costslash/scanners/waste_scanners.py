from typing import List, Dict, Any
from costslash.models import WasteItem, WasteCategory
from costslash.pricing import (
    EBS_GP2_PRICE_PER_GB,
    EBS_GP3_PRICE_PER_GB,
    EIP_MONTHLY_PENALTY,
    NAT_GATEWAY_MONTHLY_BASE,
    RDS_OFFHOURS_SAVINGS_RATIO,
    S3_STANDARD_PER_GB,
    S3_ESTIMATED_SAVINGS_RATIO,
    ECR_STORAGE_PER_GB,
)


def scan_unattached_volumes(volumes: List[Dict[str, Any]], region: str) -> List[WasteItem]:
    """Identify EBS volumes in 'available' state (not attached to any running EC2 instance)."""
    items = []
    for vol in volumes:
        state = vol.get("State", "")
        attachments = vol.get("Attachments", [])
        if state == "available" or len(attachments) == 0:
            vol_id = vol.get("VolumeId", "unknown")
            size_gb = vol.get("Size", 0)
            vol_type = vol.get("VolumeType", "gp2")
            price_per_gb = EBS_GP3_PRICE_PER_GB if vol_type == "gp3" else EBS_GP2_PRICE_PER_GB
            monthly_cost = round(size_gb * price_per_gb, 2)

            name = "unnamed"
            for tag in vol.get("Tags", []):
                if tag.get("Key") == "Name":
                    name = tag.get("Value", "unnamed")

            items.append(
                WasteItem(
                    resource_id=vol_id,
                    resource_name=name,
                    region=region,
                    category=WasteCategory.UNATTACHED_EBS,
                    details=f"{size_gb} GB ({vol_type}) unattached disk left behind",
                    monthly_waste_usd=monthly_cost,
                    recommended_action=f"Snapshot and delete unattached volume '{vol_id}'",
                    cli_command_fix=f"aws ec2 delete-volume --volume-id {vol_id} --region {region}",
                )
            )
    return items


def scan_gp2_volumes(volumes: List[Dict[str, Any]], region: str) -> List[WasteItem]:
    """Identify in-use GP2 volumes that can be upgraded to GP3 for an instant 20% cost reduction."""
    items = []
    for vol in volumes:
        state = vol.get("State", "")
        attachments = vol.get("Attachments", [])
        vol_type = vol.get("VolumeType", "")

        if vol_type == "gp2" and (state == "in-use" or len(attachments) > 0):
            vol_id = vol.get("VolumeId", "unknown")
            size_gb = vol.get("Size", 0)
            gp2_cost = size_gb * EBS_GP2_PRICE_PER_GB
            gp3_cost = size_gb * EBS_GP3_PRICE_PER_GB
            monthly_savings = round(gp2_cost - gp3_cost, 2)

            name = "unnamed"
            for tag in vol.get("Tags", []):
                if tag.get("Key") == "Name":
                    name = tag.get("Value", "unnamed")

            items.append(
                WasteItem(
                    resource_id=vol_id,
                    resource_name=name,
                    region=region,
                    category=WasteCategory.GP2_TO_GP3_MIGRATION,
                    details=f"{size_gb} GB gp2 disk (Current: ${gp2_cost:.2f}/mo -> gp3: ${gp3_cost:.2f}/mo)",
                    monthly_waste_usd=monthly_savings,
                    recommended_action=f"Modify volume type from gp2 to gp3 (zero downtime)",
                    cli_command_fix=f"aws ec2 modify-volume --volume-id {vol_id} --volume-type gp3 --region {region}",
                )
            )
    return items


def scan_unassociated_eips(addresses: List[Dict[str, Any]], region: str) -> List[WasteItem]:
    """Identify Elastic IPs allocated but not attached to an active instance or network interface."""
    items = []
    for addr in addresses:
        assoc_id = addr.get("AssociationId")
        instance_id = addr.get("InstanceId")
        if not assoc_id and not instance_id:
            alloc_id = addr.get("AllocationId", "unknown")
            public_ip = addr.get("PublicIp", "unknown")

            items.append(
                WasteItem(
                    resource_id=alloc_id,
                    resource_name=public_ip,
                    region=region,
                    category=WasteCategory.UNUSED_ELASTIC_IP,
                    details=f"Unassociated public Elastic IP ({public_ip}) incurring idle penalty",
                    monthly_waste_usd=round(EIP_MONTHLY_PENALTY, 2),
                    recommended_action=f"Release unassociated Elastic IP '{public_ip}'",
                    cli_command_fix=f"aws ec2 release-address --allocation-id {alloc_id} --region {region}",
                )
            )
    return items


def scan_nat_gateways(nat_gateways: List[Dict[str, Any]], region: str) -> List[WasteItem]:
    """Identify idle/underutilized NAT Gateways."""
    items = []
    for nat in nat_gateways:
        state = nat.get("State", "")
        if state == "available":
            nat_id = nat.get("NatGatewayId", "unknown")
            vpc_id = nat.get("VpcId", "unknown")
            name = "unnamed"
            for tag in nat.get("Tags", []):
                if tag.get("Key") == "Name":
                    name = tag.get("Value", "unnamed")

            if "idle" in name.lower() or "test" in name.lower() or "staging" in name.lower():
                items.append(
                    WasteItem(
                        resource_id=nat_id,
                        resource_name=f"{name} ({vpc_id})",
                        region=region,
                        category=WasteCategory.IDLE_NAT_GATEWAY,
                        details=f"Idle/Staging NAT Gateway costing $32.85/mo baseline running fee",
                        monthly_waste_usd=round(NAT_GATEWAY_MONTHLY_BASE, 2),
                        recommended_action=f"Consolidate VPC routing or replace with NAT Instance for staging",
                        cli_command_fix=f"aws ec2 delete-nat-gateway --nat-gateway-id {nat_id} --region {region}",
                    )
                )
    return items


def scan_rds_instances(db_instances: List[Dict[str, Any]], region: str) -> List[WasteItem]:
    """Identify Non-Production RDS databases running 24/7 that can be scheduled off-hours."""
    items = []
    for db in db_instances:
        db_id = db.get("DBInstanceIdentifier", "unknown")
        db_class = db.get("DBInstanceClass", "db.t3.medium")
        status = db.get("DBInstanceStatus", "available")
        is_multi_az = db.get("MultiAZ", False)

        # Look for dev / staging / test naming or tags
        is_non_prod = any(k in db_id.lower() for k in ["dev", "staging", "test", "demo", "sandbox"])

        if is_non_prod and status == "available":
            # Estimate monthly base cost by class
            approx_monthly = 52.0 if "medium" in db_class else (26.0 if "small" or "micro" in db_class else 105.0)
            if is_multi_az:
                approx_monthly *= 2.0  # Multi-AZ doubles instance cost

            savings = round(approx_monthly * RDS_OFFHOURS_SAVINGS_RATIO, 2)
            multi_az_warn = " (Multi-AZ in non-prod!)" if is_multi_az else ""

            items.append(
                WasteItem(
                    resource_id=db_id,
                    resource_name=f"{db_id} ({db_class}){multi_az_warn}",
                    region=region,
                    category=WasteCategory.DEV_RDS_SCHEDULING,
                    details=f"Dev database running 24/7 (Off-hours auto-sleep saves 65%)",
                    monthly_waste_usd=savings,
                    recommended_action=f"Apply nightly/weekend auto-stop schedule or convert to Single-AZ",
                    cli_command_fix=f"aws rds stop-db-instance --db-instance-identifier {db_id} --region {region}",
                )
            )
    return items


def scan_s3_buckets(buckets: List[Dict[str, Any]], region: str = "us-east-1") -> List[WasteItem]:
    """Identify S3 buckets missing lifecycle policies or Intelligent-Tiering."""
    items = []
    for b in buckets:
        name = b.get("Name", "unknown")
        has_lifecycle = b.get("HasLifecycle", True)
        estimated_size_gb = b.get("SizeGB", 200)

        if not has_lifecycle:
            potential_savings = round(estimated_size_gb * S3_STANDARD_PER_GB * S3_ESTIMATED_SAVINGS_RATIO, 2)
            items.append(
                WasteItem(
                    resource_id=name,
                    resource_name=name,
                    region=region,
                    category=WasteCategory.S3_MISSING_LIFECYCLE,
                    details=f"~{estimated_size_gb} GB paying Standard tier without Intelligent-Tiering/Glacier transition",
                    monthly_waste_usd=max(potential_savings, 2.50),
                    recommended_action=f"Enable S3 Intelligent-Tiering archive rules on bucket '{name}'",
                    cli_command_fix=f"aws s3api put-bucket-lifecycle-configuration --bucket {name} --lifecycle-configuration file://lifecycle.json",
                )
            )
    return items


def scan_ecr_repositories(repositories: List[Dict[str, Any]], region: str) -> List[WasteItem]:
    """Identify ECR repositories with untagged dangling images."""
    items = []
    for repo in repositories:
        repo_name = repo.get("repositoryName", "unknown")
        untagged_count = repo.get("untaggedImageCount", 0)
        estimated_waste_gb = repo.get("untaggedSizeGB", 15)

        if untagged_count > 0:
            monthly_cost = round(estimated_waste_gb * ECR_STORAGE_PER_GB, 2)
            items.append(
                WasteItem(
                    resource_id=repo_name,
                    resource_name=repo_name,
                    region=region,
                    category=WasteCategory.ECR_UNTAGGED_IMAGES,
                    details=f"{untagged_count} untagged/dangling image layers (~{estimated_waste_gb} GB)",
                    monthly_waste_usd=max(monthly_cost, 1.50),
                    recommended_action=f"Apply ECR lifecycle policy to expire untagged images older than 7 days",
                    cli_command_fix=f"aws ecr put-lifecycle-policy --repository-name {repo_name} --region {region} --lifecycle-policy-text file://ecr-policy.json",
                )
            )
    return items
