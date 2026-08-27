# 💰 CostSlash

> **Instant AWS Cloud Cost & Waste Optimization Scanner**

CostSlash scans your AWS infrastructure in seconds to find forgotten zombie resources, unattached disks, idle NAT gateways, and unassociated Elastic IPs—showing you the exact dollar savings and 1-click remediation commands.

---

## ⚡ Quickstart

### 1. Run a Scan with Instant Demo Data (No AWS Account Needed)
```bash
python -m costslash.cli demo
```

### 2. Scan a Live AWS Account (100% Read-Only & Free)
```bash
# Uses your default AWS CLI credentials (~/.aws/credentials)
python -m costslash.cli scan --live --region us-east-1

# With a specific AWS profile
python -m costslash.cli scan --live --profile my-client --region us-east-1 --fix
```

### 3. Export Savings Report to JSON
```bash
python -m costslash.cli scan --export-json savings-report.json
```

---

## 🔍 What CostSlash Scans
1. **Unattached EBS Volumes:** Disks left behind after deleting EC2 instances.
2. **GP2 to GP3 Upgrades:** Upgrading older GP2 volumes to modern GP3 for instant 20% savings + faster performance with zero downtime.
3. **Unassociated Elastic IPs:** Public IPs incurring AWS idle penalty charges.
4. **Idle NAT Gateways:** NAT Gateways in staging/idle VPCs ($32.85/mo each).
