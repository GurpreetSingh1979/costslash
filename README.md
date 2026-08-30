# ⚡ CostSlash

> **Instant AWS Cloud Cost & Waste Optimization Scanner**

[![PyPI version](https://img.shields.io/pypi/v/costslash.svg)](https://pypi.org/project/costslash/)
[![PyPI Downloads](https://static.pepy.tech/badge/costslash)](https://pepy.tech/project/costslash)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CostSlash scans your AWS infrastructure in seconds to find forgotten zombie resources, unattached disks, idle NAT gateways, and unassociated Elastic IPs—showing you the exact dollar savings and 1-click remediation commands.

🌐 **Live Web Platform & FinOps Booking:** [https://costslash-web.vercel.app](https://costslash-web.vercel.app)

---

## ⚡ Quickstart

### 1. Install via pip
```bash
pip install costslash
```

### 2. Run Instant Demo Scan (Zero AWS credentials needed)
```bash
costslash demo
# or (Windows / cross-platform fallback)
python -m costslash demo
```

### 3. Scan a Live AWS Account (100% Free & Read-Only)
```bash
# Scan across all AWS regions in parallel with 1-click cleanup commands
costslash scan --live --all-regions --fix

# or on Windows Command Prompt / PowerShell:
python -m costslash scan --live --all-regions --fix

# Scan a single specific region:
costslash scan --live --region us-east-1 --fix

# Scan using a specific AWS CLI profile:
costslash scan --live --all-regions --profile production --fix
```

### 4. Export Savings Report to JSON
```bash
costslash scan --live --all-regions -o savings-report.json
# or
python -m costslash scan --live --all-regions -o savings-report.json
```

---

## 💻 Windows Troubleshooting

If you see `'costslash' is not recognized as an internal or external command`:
Run with **`python -m`** in front:
```cmd
python -m costslash scan --live --all-regions --fix
```
Or add Python's `Scripts` folder to your Windows User `PATH` environment variable.

---

## 🔍 What CostSlash Audits
1. **Amazon EBS:** Unattached orphaned volumes + `gp2` $\rightarrow$ `gp3` instant 20% price cut upgrades.
2. **Amazon VPC:** Unassociated Elastic IPs + Idle NAT Gateways ($32.85/mo each).
3. **Amazon RDS:** Non-production dev/staging databases running 24/7 (weekend scheduling saves **65%**).
4. **Amazon S3:** Buckets paying standard tier for cold data without Intelligent-Tiering / Glacier rules.
5. **Amazon ECR:** Untagged / dangling Docker image layers consuming repository storage.

---

## 🔒 Security Guarantee
- **100% Read-Only:** Calls only read-only AWS metadata APIs.
- **Zero Credentials Stored:** Uses your active local authenticated AWS CLI session.
- **Client-Side:** Zero telemetry or data is sent to external servers.

---

## 📄 License
MIT License. Built with ❤️ for Cloud Engineers and DevOps teams.
