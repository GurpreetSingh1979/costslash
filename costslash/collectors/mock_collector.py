from typing import Dict, Any, List
from costslash.models import ScanReport
from costslash.scanners.waste_scanners import (
    scan_unattached_volumes,
    scan_gp2_volumes,
    scan_unassociated_eips,
    scan_nat_gateways,
)


def get_mock_aws_payload() -> Dict[str, List[Dict[str, Any]]]:
    """Generates realistic AWS API response payloads with typical startup waste."""
    return {
        "volumes": [
            # 2 Unattached EBS volumes
            {
                "VolumeId": "vol-0a1b2c3d4e5f001",
                "Size": 250,
                "VolumeType": "gp2",
                "State": "available",
                "Attachments": [],
                "Tags": [{"Key": "Name", "Value": "old-postgres-backup-volume"}],
            },
            {
                "VolumeId": "vol-0a1b2c3d4e5f002",
                "Size": 100,
                "VolumeType": "gp3",
                "State": "available",
                "Attachments": [],
                "Tags": [{"Key": "Name", "Value": "temp-analytics-worker-disk"}],
            },
            # 3 In-use GP2 volumes eligible for GP3 upgrade (save 20%)
            {
                "VolumeId": "vol-0a1b2c3d4e5f003",
                "Size": 500,
                "VolumeType": "gp2",
                "State": "in-use",
                "Attachments": [{"InstanceId": "i-0123456789abcdef0"}],
                "Tags": [{"Key": "Name", "Value": "production-api-root-disk"}],
            },
            {
                "VolumeId": "vol-0a1b2c3d4e5f004",
                "Size": 1000,
                "VolumeType": "gp2",
                "State": "in-use",
                "Attachments": [{"InstanceId": "i-0123456789abcdef1"}],
                "Tags": [{"Key": "Name", "Value": "elasticsearch-data-node-1"}],
            },
            {
                "VolumeId": "vol-0a1b2c3d4e5f005",
                "Size": 1000,
                "VolumeType": "gp2",
                "State": "in-use",
                "Attachments": [{"InstanceId": "i-0123456789abcdef2"}],
                "Tags": [{"Key": "Name", "Value": "elasticsearch-data-node-2"}],
            },
        ],
        "addresses": [
            # 2 Unassociated Elastic IPs
            {
                "AllocationId": "eipalloc-0123456789abcdef0",
                "PublicIp": "54.210.45.12",
                "Domain": "vpc",
            },
            {
                "AllocationId": "eipalloc-0123456789abcdef1",
                "PublicIp": "52.86.110.99",
                "Domain": "vpc",
            },
            # 1 Associated Elastic IP (Not waste)
            {
                "AllocationId": "eipalloc-0123456789abcdef2",
                "PublicIp": "34.195.80.201",
                "AssociationId": "eipassoc-0123456789abcdef2",
                "InstanceId": "i-0123456789abcdef0",
                "Domain": "vpc",
            },
        ],
        "nat_gateways": [
            # 1 Idle NAT Gateway in staging VPC
            {
                "NatGatewayId": "nat-0123456789abcdef0",
                "VpcId": "vpc-0987654321fedcba0",
                "State": "available",
                "Tags": [{"Key": "Name", "Value": "staging-idle-nat-gateway"}],
            }
        ],
    }


def run_mock_scan(region: str = "us-east-1", account_id: str = "123456789012 (Demo Account)") -> ScanReport:
    """Runs a full scan across the mock AWS payload."""
    payload = get_mock_aws_payload()
    items = []
    
    items.extend(scan_unattached_volumes(payload["volumes"], region=region))
    items.extend(scan_gp2_volumes(payload["volumes"], region=region))
    items.extend(scan_unassociated_eips(payload["addresses"], region=region))
    items.extend(scan_nat_gateways(payload["nat_gateways"], region=region))

    return ScanReport(
        account_id=account_id,
        scan_timestamp="2026-08-27 16:20:00 UTC",
        region=region,
        items=items,
    )
