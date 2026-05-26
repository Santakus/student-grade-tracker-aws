# Project 10: Serverless Contact Form with Email 

## Architecture Overview

```
┌──────────┐     ┌──────────┐     ┌───────────────┐     ┌──────────┐     ┌──────────────┐
│  Browser  │────▶│  S3      │     │  API Gateway  │────▶│  Lambda  │────▶│  DynamoDB    │
│  (User)   │     │ (Static  │────▶│  (REST API)   │     │ Function │     │ (Submissions)│
│           │     │  Site)   │     └───────────────┘     └──────────┘     └──────────────┘
└──────────┘     └──────────┘                                 │
                                                              ▼
                                                        ┌──────────┐
                                                        │   SES    │
                                                        │ (Email)  │
                                                        └──────────┘
```

**Estimated Cost**: Free Tier eligible (SES: 62K emails/month free from Lambda, DynamoDB: 25GB free)