# 💰 CostSlash

> **Instant AWS Cloud Cost & Waste Optimization Scanner**

[![PyPI version](https://img.shields.io/pypi/v/costslash.svg)](https://pypi.org/project/costslash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CostSlash scans your AWS infrastructure in seconds to find forgotten zombie resources, unattached disks, idle NAT gateways, and unassociated Elastic IPs—showing you the exact dollar savings and 1-click remediation commands.

---

## ⚡ Quickstart

### 1. Install via pip
```bash
pip install costslash
```

### 2. Run Instant Demo Scan (Zero AWS account needed)
```bash
costslash demo
# or
python -m costslash demo
# or
pipx run costslash demo
```

### 3. Scan a Live AWS Account (100% Free & Read-Only)
```bash
# Scan across all AWS regions in parallel
costslash scan --live --all-regions

# Scan with 1-click CLI cleanup commands
costslash scan --live --all-regions --fix
```

### 4. Export Savings Report to JSON
```bash
costslash scan --export-json savings-report.json
```

---

## 🔍 What CostSlash Scans
1. **Amazon EBS:** Unattached volumes + `gp2` $\rightarrow$ `gp3` instant 20% price cuts.
2. **Amazon VPC:** Unassociated Elastic IPs + Idle NAT Gateways.
3. **Amazon RDS:** Non-production dev/staging databases running 24/7 (scheduling saves **65%**).
4. **Amazon S3:** Buckets paying standard tier for cold data without Intelligent-Tiering / Glacier lifecycle rules.
5. **Amazon ECR:** Untagged / dangling Docker image layers consuming repository storage.
