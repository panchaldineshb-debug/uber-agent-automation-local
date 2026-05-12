# Uber Agent Automation — Local-First Mac

My son Sameer needs Uber ride from his school everyday either at 2:35 or 4 PM EST (Inside JP Steven School, Edison, NJ 08820), what can he do by sending email so that claude code skills and agents can help him, be simple, honest and highly technical.

Polls Gmail for ride-request emails from a designated sender, parses the intended ride time, calls the Uber API, and sends SMS + macOS notifications.

Runs as a macOS \`launchd\` service on an M4 Mac.

## Architecture

\`\`\`
uber-agent-automation-local/
│
├── Core Config / Infra
│   ├── .env
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── uv.lock
│   ├── Makefile
│   ├── .python-version
│   ├── client_secrets.json
│   ├── com.sarabilabs.rideagent.plist
│   └── core/
│       ├── __init__.py
│       ├── settings.py
│       ├── logger.py
│       └── monitoring.py
│
├── Agent Layer
│   └── agents/
│       └── local_worker.py   ← MAIN ORCHESTRATOR (critical file)
│
├── Skills Layer
│   ├── skills/
│   │   ├── email_parser/
│   │   │   └── handler.py
│   │   ├── ride_request/
│   │   │   ├── handler.py
│   │   │   └── SKILL.md
│   │   ├── notifier/
│   │   │   ├── handler.py
│   │   │   └── mac_alert.py
│   │   ├── email_reply/
│   │   │   └── handler.py
│   │   ├── gmail_auth/
│   │   │   └── handler.py
│
├── Scripts / Ops Tools
│   ├── scripts/
│   │   ├── uber_login.py
│   │   ├── use_uber_session.py
│   │   ├── auth_setup.py
│   │   └── check_session.py
│
├── Observability (minimal)
│   └── logs/
│       ├── stdout.log
│       └── stderr.log
│
└── Runtime state
    └── config/
        └── uber_state.json
\`\`\`

## Commands

| Task | Command |
|------|---------|
| Run worker (dev) | \`python3 -m agents.local_worker\` |
| Run with uv | \`uv run python agents/local_worker.py\` |
| One-time OAuth setup | \`make auth-init\` |
| Seed secrets to Keychain | \`make seed-secrets\` |
| Install as launchd service | \`make setup && make load\` |
| Restart service | \`make reload\` |
| Check service status | \`make status\` |
| Tail logs | \`make logs\` |
| Run tests | \`make test\` |

## Secrets & Auth

All secrets live in **macOS Keychain** under service name \`SarabiLabs_Uber_Automator\`. Keys: \`google_client_id\`, \`google_client_secret\`, \`gmail_app_password\`, \`twilio_sid\`, \`twilio_token\`, \`twilio_phone\`, \`son_phone\`, \`uber_server_token\`, \`home_address\`. Seed them with \`make seed-secrets\`. Never store secrets in \`.env\` or code.

Google OAuth tokens are written to disk by \`scripts/auth_setup.py\` (one-time browser flow). The worker reads them at startup via \`skills/gmail_auth/handler.py\`.

## Conventions

- \`skills/\` are stateless, independently testable units. No polling logic inside them.
- \`agents/local_worker.py\` owns the loop, IMAP connection, and skill orchestration.
- Use \`imaplib\` for Gmail (IMAP/IDLE), \`requests\` for Uber API, \`twilio\` for SMS.
- No boto3 or AWS SDK — this is a local-first project.
- Logs go to \`logs/stdout.log\` and \`logs/stderr.log\` (managed by launchd).

## Key Config

- Poll interval: 300s (5 min) — defined in \`agents/local_worker.py\`
- Hardcoded pickup coords: \`40.5482, -74.3444\` (JP Stevens HS)
- Sender filter: \`SON_EMAIL\` — defined in \`core/settings.py\`