# Project 3: Full-Stack App on Elastic Beanstalk — Deep Dive

## Architecture Overview

```
┌──────────┐     ┌───────────────────────────────────────┐
│  Browser  │────▶│       Elastic Beanstalk Environment    │
│  (User)   │◀────│  ┌─────────────┐  ┌───────────────┐  │
└──────────┘     │  │   EC2 + App  │──│  RDS PostgreSQL│  │
                 │  │  (Node.js)   │  │  (Private)     │  │
                 │  └─────────────┘  └───────────────┘  │
                 │       Security Group Layering          │
                 └───────────────────────────────────────┘
```

**Application**: Student Grade Tracker (Node.js + Express + EJS + PostgreSQL)

**Estimated Cost**: ~$1-2/day outside Free Tier (t3.micro EC2 + db.t3.micro RDS). Free Tier: t2.micro EC2 free for 12 months, db.t3.micro RDS free for 12 months.

---