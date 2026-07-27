# Project 2: Serverless Task Manager API

## 📋 Project Overview

In this project, you will build a **fully serverless REST API** that manages tasks (to-dos). The system uses **AWS Lambda** for compute, **API Gateway** to expose HTTP endpoints, and **DynamoDB** as a NoSQL database — with zero servers to manage.

By the end, you will have a working API that supports full **CRUD operations** (Create, Read, Update, Delete) accessible from any HTTP client like curl, Postman, or a web browser.

---

## Architecture Overview

```
┌──────────┐     ┌───────────────┐     ┌──────────┐     ┌──────────────┐
│  Client   │────▶│  API Gateway  │────▶│  Lambda  │────▶│  DynamoDB    │
│ (curl/    │◀────│  (REST API)   │◀────│ Function │◀────│  (TaskTable) │
│  Postman) │     └───────────────┘     └──────────┘     └──────────────┘
└──────────┘                                │
                                            ▼
                                     ┌──────────────┐
                                     │  CloudWatch  │
                                     │   (Logs)     │
                                     └──────────────┘
```

**API Endpoints**:
| Method | Path | Description |
|--------|------|-------------|
| GET | `/tasks` | List all tasks (optional `?status=` filter) |
| GET | `/tasks/{id}` | Get a specific task |
| POST | `/tasks` | Create a new task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |

**Estimated Cost**: Free Tier eligible (Lambda: 1M requests/month free, DynamoDB: 25GB free)