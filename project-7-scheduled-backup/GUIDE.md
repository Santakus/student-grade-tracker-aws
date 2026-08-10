# Project 7: Scheduled Backup & Notification System — Deep Dive

## Architecture Overview

```
┌──────────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  EventBridge │────▶│  Lambda  │────▶│  S3      │     │  S3      │
│  (Schedule)  │     │ (Backup) │     │ (Source) │────▶│ (Backup) │
└──────────────┘     └──────────┘     └──────────┘     └──────────┘
                          │
                          ▼
                    ┌──────────┐
                    │   SNS    │
                    │ (Email)  │
                    └──────────┘
```

**Estimated Cost**: Free Tier eligible

---

## 🏗️ Architecture

```
EventBridge (Cron: every 6 hours) → Lambda (Backup Function)
                                         ├── Reads from S3 Source Bucket
                                         ├── Copies to S3 Backup Bucket
                                         └── Sends report via SNS → Email
```

| Component        | AWS Service     | Purpose                                     |
|------------------|-----------------|----------------------------------------------|
| Scheduler        | EventBridge     | Triggers backup on a cron schedule           |
| Compute          | Lambda          | Copies files from source to backup bucket    |
| Source Storage    | S3              | Holds the original files to be backed up     |
| Backup Storage   | S3              | Stores timestamped backup copies             |
| Notifications    | SNS             | Sends email reports after each backup run    |
| Access Control   | IAM             | Grants Lambda read/write/publish permissions |

