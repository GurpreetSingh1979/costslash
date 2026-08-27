from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class WasteCategory(str, Enum):
    UNATTACHED_EBS = "Unattached EBS Volumes"
    GP2_TO_GP3_MIGRATION = "Legacy GP2 Volume Upgrades"
    UNUSED_ELASTIC_IP = "Unassociated Elastic IPs"
    IDLE_NAT_GATEWAY = "Idle / Underutilized NAT Gateways"
    DEV_RDS_SCHEDULING = "Dev/Staging RDS 24/7 Running"
    S3_MISSING_LIFECYCLE = "S3 Missing Lifecycle / Cold Data"
    ECR_UNTAGGED_IMAGES = "ECR Untagged / Stale Docker Layers"


class WasteItem(BaseModel):
    resource_id: str
    resource_name: str
    region: str
    category: WasteCategory
    details: str
    monthly_waste_usd: float = Field(ge=0.0)
    recommended_action: str
    cli_command_fix: Optional[str] = None


class ScanReport(BaseModel):
    account_id: str
    scan_timestamp: str
    region: str
    items: List[WasteItem] = Field(default_factory=list)

    @property
    def total_monthly_savings(self) -> float:
        return sum(item.monthly_waste_usd for item in self.items)

    @property
    def total_yearly_savings(self) -> float:
        return self.total_monthly_savings * 12

    @property
    def waste_by_category(self) -> Dict[str, float]:
        summary: Dict[str, float] = {}
        for item in self.items:
            cat_name = item.category.value
            summary[cat_name] = summary.get(cat_name, 0.0) + item.monthly_waste_usd
        return summary
