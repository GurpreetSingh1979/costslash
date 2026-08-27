"""
AWS Standard Reference Pricing (us-east-1 baseline in USD)
"""

# EBS Storage pricing per GB-month
EBS_GP2_PRICE_PER_GB = 0.10      # $0.10 / GB-month
EBS_GP3_PRICE_PER_GB = 0.08      # $0.08 / GB-month (20% cheaper than gp2)

# Elastic IP pricing for unassociated / idle IPs
EIP_UNASSOCIATED_HOURLY_PENALTY = 0.005  # $0.005 / hour
EIP_MONTHLY_PENALTY = EIP_UNASSOCIATED_HOURLY_PENALTY * 730  # ~$3.65 / month

# NAT Gateway base running fee (excluding data processing)
NAT_GATEWAY_HOURLY_COST = 0.045  # $0.045 / hour
NAT_GATEWAY_MONTHLY_BASE = NAT_GATEWAY_HOURLY_COST * 730   # ~$32.85 / month

# RDS Database pricing (Savings from off-hours stop: 65% reduction on 730h/mo)
RDS_OFFHOURS_SAVINGS_RATIO = 0.65  # Turning off 7pm-7am + weekends saves 65%

# S3 Standard vs Intelligent-Tiering cold storage estimated monthly savings per 100GB
S3_STANDARD_PER_GB = 0.023
S3_INFREQUENT_ACCESS_PER_GB = 0.0125
S3_ESTIMATED_SAVINGS_RATIO = 0.40  # ~40% savings on cold bucket data

# ECR Storage per GB-month
ECR_STORAGE_PER_GB = 0.10
