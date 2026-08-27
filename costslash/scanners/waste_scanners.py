from typing import List, Dict, Any
from costslash.models import WasteItem, WasteCategory
from costslash.pricing import (
    EBS_GP2_PRICE_PER_GB,
    EBS_GP3_PRICE_PER_GB,
    EIP_MONTHLY_PENALTY,
    NAT_GATEWAY_MONTHLY_BASE,
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
        
        # Only in-use attached volumes should be upgraded (unattached ones should be deleted)
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
