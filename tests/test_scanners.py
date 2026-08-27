import unittest
from costslash.collectors.mock_collector import run_mock_scan
from costslash.models import WasteCategory


class TestCostSlashScanners(unittest.TestCase):
    def setUp(self):
        self.report = run_mock_scan(region="us-east-1")

    def test_total_savings_calculated(self):
        self.assertGreater(self.report.total_monthly_savings, 50.0)
        self.assertGreater(self.report.total_yearly_savings, 600.0)

    def test_unattached_ebs_detected(self):
        ebs_items = [i for i in self.report.items if i.category == WasteCategory.UNATTACHED_EBS]
        self.assertEqual(len(ebs_items), 2)
        # 250GB gp2 ($25) + 100GB gp3 ($8) = $33.00
        total_ebs_waste = sum(i.monthly_waste_usd for i in ebs_items)
        self.assertEqual(total_ebs_waste, 33.0)

    def test_gp2_upgrade_savings(self):
        gp2_items = [i for i in self.report.items if i.category == WasteCategory.GP2_TO_GP3_MIGRATION]
        self.assertEqual(len(gp2_items), 3)
        # 500GB ($10 save) + 1000GB ($20 save) + 1000GB ($20 save) = $50.00
        total_gp2_savings = sum(i.monthly_waste_usd for i in gp2_items)
        self.assertEqual(total_gp2_savings, 50.0)

    def test_unassociated_eips_detected(self):
        eip_items = [i for i in self.report.items if i.category == WasteCategory.UNUSED_ELASTIC_IP]
        self.assertEqual(len(eip_items), 2)

    def test_nat_gateway_detected(self):
        nat_items = [i for i in self.report.items if i.category == WasteCategory.IDLE_NAT_GATEWAY]
        self.assertEqual(len(nat_items), 1)


if __name__ == "__main__":
    unittest.main()
