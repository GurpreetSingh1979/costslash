"""
AWS Standard Reference Pricing (us-east-1 baseline in USD)
"""

# EBS Storage pricing per GB-month
EBS_GP2_PRICE_PER_GB = 0.10      # $0.10 / GB-month
EBS_GP3_PRICE_PER_GB = 0.08      # $0.08 / GB-month (20% cheaper than gp2)
EBS_IO1_PRICE_PER_GB = 0.125
EBS_STANDARD_PRICE_PER_GB = 0.05

# Elastic IP pricing for unassociated / idle IPs
EIP_UNASSOCIATED_HOURLY_PENALTY = 0.005  # $0.005 / hour
EIP_MONTHLY_PENALTY = EIP_UNASSOCIATED_HOURLY_PENALTY * 730  # ~$3.65 / month

# NAT Gateway base running fee (excluding data processing)
NAT_GATEWAY_HOURLY_COST = 0.045  # $0.045 / hour
NAT_GATEWAY_MONTHLY_BASE = NAT_GATEWAY_HOURLY_COST * 730   # ~$32.85 / month

# EBS Snapshot standard storage per GB-month
EBS_SNAPSHOT_PRICE_PER_GB = 0.05  # $0.05 / GB-month
