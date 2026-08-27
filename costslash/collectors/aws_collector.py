from datetime import datetime, timezone
from typing import Optional
from costslash.models import ScanReport
from costslash.scanners.waste_scanners import (
    scan_unattached_volumes,
    scan_gp2_volumes,
    scan_unassociated_eips,
    scan_nat_gateways,
)


def run_live_aws_scan(region: str = "us-east-1", profile: Optional[str] = None) -> ScanReport:
    """Connects to real AWS account via boto3 and performs a 100% read-only cost audit."""
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, PartialCredentialsError
    except ImportError:
        raise RuntimeError("boto3 is required for live scans. Run: pip install boto3")

    session = boto3.Session(profile_name=profile, region_name=region) if profile else boto3.Session(region_name=region)

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

    ec2_client = session.client("ec2", region_name=region)
    items = []

    # 1. Fetch EBS Volumes
    try:
        volumes_resp = ec2_client.describe_volumes()
        volumes = volumes_resp.get("Volumes", [])
        items.extend(scan_unattached_volumes(volumes, region=region))
        items.extend(scan_gp2_volumes(volumes, region=region))
    except Exception as e:
        pass

    # 2. Fetch Elastic IPs
    try:
        eips_resp = ec2_client.describe_addresses()
        addresses = eips_resp.get("Addresses", [])
        items.extend(scan_unassociated_eips(addresses, region=region))
    except Exception as e:
        pass

    # 3. Fetch NAT Gateways
    try:
        nats_resp = ec2_client.describe_nat_gateways()
        nat_gateways = nats_resp.get("NatGateways", [])
        items.extend(scan_nat_gateways(nat_gateways, region=region))
    except Exception as e:
        pass

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return ScanReport(
        account_id=account_id,
        scan_timestamp=now_utc,
        region=region,
        items=items,
    )
