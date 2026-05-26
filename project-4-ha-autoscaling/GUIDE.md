# Project 4: Highly Available Web App with Auto Scaling 

## Architecture Overview

```
                        ┌─── Availability Zone A ────┐  ┌─── Availability Zone B ────┐
                        │                             │  │                             │
Internet ──▶ IGW ──▶   │  ┌─────────────────────┐   │  │  ┌─────────────────────┐   │
                        │  │   Public Subnet A    │   │  │  │   Public Subnet B    │   │
              │         │  │  ┌───────────────┐   │   │  │  │  ┌───────────────┐   │   │
              ▼         │  │  │   NAT Gateway │   │   │  │  │  │               │   │   │
        ┌─────────┐     │  │  └───────────────┘   │   │  │  │  │               │   │   │
        │   ALB   │────▶│  └─────────────────────┘   │  │  └─────────────────────┘   │
        └─────────┘     │  ┌─────────────────────┐   │  │  ┌─────────────────────┐   │
                        │  │   Private Subnet A   │   │  │  │   Private Subnet B   │   │
                        │  │  ┌──────┐ ┌──────┐   │   │  │  │  ┌──────┐ ┌──────┐   │   │
                        │  │  │ EC2  │ │ RDS  │   │   │  │  │  │ EC2  │ │ RDS  │   │   │
                        │  │  │(ASG) │ │Primary│  │   │  │  │  │(ASG) │ │Standby│  │   │
                        │  │  └──────┘ └──────┘   │   │  │  │  └──────┘ └──────┘   │   │
                        │  └─────────────────────┘   │  │  └─────────────────────┘   │
                        └─────────────────────────────┘  └─────────────────────────────┘
```

**Estimated Cost**: ~$3-5/day (ALB + 2x t3.micro + db.t3.micro + NAT Gateway)