# Project 5: Event-Driven Image Processing Pipeline 

## Architecture Overview

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────────┐     ┌──────────────┐
│  User     │     │  Input   │     │   SQS    │     │   Lambda     │     │   Output     │
│  Uploads  │────▶│  S3      │────▶│  Queue   │────▶│  Processor   │────▶│   S3         │
│  Image    │     │  Bucket  │     │          │     │  (Pillow)    │     │   (Thumbs)   │
└──────────┘     └──────────┘     └──────────┘     └──────────────┘     └──────────────┘
                                       │                   │
                                       ▼                   ├──────▶ DynamoDB (Metadata)
                                  ┌──────────┐             │
                                  │   DLQ    │             └──────▶ SNS (Email Alert)
                                  │  (Failed)│
                                  └──────────┘
```

**Estimated Cost**: Free Tier eligible (Lambda: 1M requests/month, S3: 5GB, SQS: 1M requests, DynamoDB: 25GB)