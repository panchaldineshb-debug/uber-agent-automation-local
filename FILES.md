# Tree Structure used for Local

## Ignore infra which was used for aws cloud

```
uber-agent-automation-local/
├── CLAUDE.md                # AI orchestration & project rules
├── agents/                  # Logic for "Intent Recognition" 
│   └── ride_scheduler.py    # Python agent for processing ride requests
├── skills/                  # Core functional tools (Claude Skills)
│   ├── ride_request/        # Uber API logic
│   └── email_parser/        # SES/S3 parsing logic
├── infra/                   # AWS Serverless IaC (CDKTF/Terraform)
│   ├── main.py              # Entry point for AWS resources
│   └── stacks_constructs/   # Reusable constructs (Lambda, SES, S3)
├── requirements.txt         # Project dependencies (boto3, requests, etc.)
└── .claude/                 # Claude-specific internal configurations
```