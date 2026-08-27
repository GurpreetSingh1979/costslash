from datetime import datetime, timezone
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from costslash.models import ScanReport, WasteItem
from costslash.scanners.waste_scanners import (
    scan_unattached_volumes,
    scan_gp2_volumes,
    scan_unassociated_eips,
    scan_nat_gateways,
)


def _scan_single_region(session, region: str) -> List[WasteItem]:
    """Helper to scan a single AWS region for EBS, EIP, and NAT waste."""
    items: List[WasteItem] = []
    try:
        ec2_client = session.client("ec2", region_name=region)

        # 1. EBS Volumes
        try:
            volumes_resp = ec2_client.describe_volumes()
            volumes = volumes_resp.get("Volumes", [])
            items.extend(scan_unattached_volumes(volumes, region=region))
            items.extend(scan_gp2_volumes(volumes, region=region))
        except Exception:
            pass

        # 2. Elastic IPs
        try:
            eips_resp = ec2_client.describe_addresses()
            addresses = eips_resp.get("Addresses", [])
            items.extend(scan_unassociated_eips(addresses, region=region))
        except Exception:
            pass

        # 3. NAT Gateways
        try:
            nats_resp = ec2_client.describe_nat_gateways()
            nat_gateways = nats_resp.get("NatGateways", [])
            items.extend(scan_nat_gateways(nat_gateways, region=region))
        except Exception:
            pass
    except Exception:
        pass

    return items


def run_live_aws_scan(
    region: str = "us-east-1",
    all_regions: bool = False,
    profile: Optional[str] = None,
) -> ScanReport:
    """Connects to real AWS account via boto3 and performs a 100% read-only cost audit."""
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, PartialCredentialsError
    except ImportError:
        raise RuntimeError("boto3 is required for live scans. Run: pip install boto3")

    session = (
        boto3.Session(profile_name=profile, region_name=region)
        if profile
        else boto3.Session(region_name=region)
    )

    try:
        sts_client = session.client("sts")
        caller_identity = sts_client.get_caller_identity()
        account_id = caller_identity.get("Account", "unknown-account")
    except (NoCredentialsError, PartialCredentialsError) as e:
        raise RuntimeError(
            "AWS credentials not found. Please run 'aws configure' or pass an active AWS profile."
        ) from e
    except Exception as e:
        account_id = f"AWS-Account ({str(e)[:30]}...)"

    all_items: List[WasteItem] = []
    target_region_label = region

    if all_regions:
        target_region_label = "ALL Regions"
        try:
            ec2_main = session.client("ec2", region_name="us-east-1")
            regions_resp = ec2_main.describe_regions(
                Filters=[{"Name": "opt-in-status", "Values": ["opt-in-not-required", "opted-in"]}]
            )
            available_regions = [r["RegionName"] for r in regions_resp.get("Regions", [])]
        except Exception:
            available_regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "ap-south-1", "eu-west-1"]

        # Fast parallel scan across all regions using thread pool
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_region = {
                executor.submit(_scan_single_region, session, r): r for r in available_regions
            }
            for future in as_completed(future_to_region):
                items = future.result()
                all_items.extend(items)
    else:
        all_items = _scan_single_region(session, region)

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return ScanReport(
        account_id=account_id,
        scan_timestamp=now_utc,
        region=target_region_label,
        items=all_items,
    )
