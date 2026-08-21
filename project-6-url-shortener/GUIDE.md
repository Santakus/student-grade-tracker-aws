# Project 6: Serverless URL Shortener — Deep Dive

## Architecture Overview

```
┌──────────┐     ┌──────────┐                    ┌───────────────┐     ┌──────────┐     ┌──────────────┐
│  Browser  │────▶│  S3      │                    │  API Gateway  │────▶│  Lambda  │────▶│  DynamoDB    │
│  (User)   │◀────│ (Static  │───── API Calls ───▶│  (REST API)   │◀────│ Function │◀────│ (URL Table)  │
│           │     │  Site)   │                    └───────────────┘     └──────────┘     └──────────────┘
└──────────┘     └──────────┘
```

**Endpoints**:
| Method | Path | Description |
|--------|------|-------------|
| POST | `/shorten` | Create a short URL |
| GET | `/{code}` | Redirect to original URL (301) |
| GET | `/stats/{code}` | Get click statistics |

**Estimated Cost**: Free Tier eligible