### Static Portfolio Website

## Architecture Overview

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Browser    │──────▶│  CloudFront  │──────▶│   S3 Bucket  │
│   (User)     │◀──────│  (CDN/HTTPS) │◀──────│ (Static Host)│
└──────────────┘       └──────────────┘       └──────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │     OAC      │
                       │ (Access Ctrl)│
                       └──────────────┘
```

**Key Services**: Amazon S3, Amazon CloudFront, AWS IAM

**Estimated Cost**: Free Tier eligible (S3: 5GB free, CloudFront: 1TB/month free for 12 months)