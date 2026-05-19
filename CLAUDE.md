# Uber Agent Automation — Local-First Mac

My son Sameer needs Uber ride from his school everyday either at 2:35 or 4 PM EST (Inside JP Steven School, Edison, NJ 08820), what can he do by sending email so that claude code skills and agents can help him, be simple, honest and highly technical.

Polls Gmail for ride-request emails from a designated sender, parses the intended ride time, automates Uber booking via Playwright browser session, and sends SMS + macOS notifications.

Sameer sends an email (WhatsApp planned, not implemented) to trigger a ride from school at 2:35 or 4 PM EST (JP Stevens HS, Edison, NJ 08820).

All rides are restricted to Edison, NJ zip codes {08817, 08820, 08837, 08899} via geocoder bounding box. Max 2 rides per day enforced by `skills/rate_limiter/handler.py` (state in `config/ride_count.json`).

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
│       ├── monitoring.py
│       └── geocoder.py
│
├── Agent Layer
│   └── agents/
│       ├── local_worker.py      ← MAIN ORCHESTRATOR (critical file)
│       ├── health_monitor.py    ← launchd + session + disk checks
│       ├── retry_agent.py       ← exponential backoff wrapper
│       ├── session_agent.py     ← file-level Uber session state (no Playwright)
│       └── CLAUDE.md
│
├── Skills Layer
│   └── skills/
│       ├── email_parser/
│       │   ├── handler.py
│       │   └── SKILL.md
│       ├── ride_request/
│       │   ├── handler.py
│       │   └── SKILL.md
│       ├── rate_limiter/        ← NEW: max 2 rides/day enforcement
│       │   ├── handler.py
│       │   └── SKILL.md
│       ├── ride_scheduler/      ← NEW: validate 2:35/4PM slots (±10 min)
│       │   ├── handler.py
│       │   └── SKILL.md
│       ├── session_manager/     ← NEW: Playwright + file session checks
│       │   ├── handler.py
│       │   └── SKILL.md
│       ├── uber_eta/            ← NEW: fetch ETAs without booking
│       │   ├── handler.py
│       │   └── SKILL.md
│       ├── notifier/
│       │   ├── handler.py
│       │   ├── mac_alert.py
│       │   └── SKILL.md
│       ├── email_reply/
│       │   ├── handler.py
│       │   └── SKILL.md
│       ├── gmail_auth/
│       │   ├── handler.py
│       │   └── SKILL.md
│       └── gmail_precheck/
│           ├── handler.py
│           └── SKILL.md
│
├── Scripts / Ops Tools
│   └── scripts/
│       ├── uber_login.py
│       ├── use_uber_session.py
│       ├── auth_setup.py
│       ├── check_session.py
│       └── mcp_server.py        ← NEW: MCP plugin (4 status tools for Claude)
│
├── Observability (minimal)
│   └── logs/
│       ├── stdout.log
│       ├── stderr.log
│       └── hook.log             ← NEW: Claude Code hook events
│
└── Runtime state
    └── config/
        ├── uber_state.json      ← Playwright session cookies
        └── ride_count.json      ← NEW: daily ride count for rate limiter
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
| MCP server (Claude tools) | \`uv run python scripts/mcp_server.py\` |
| Health check | \`uv run python -c "from agents.health_monitor import HealthMonitor; print(HealthMonitor().run_all())"\` |

## Secrets & Auth

All secrets live in **macOS Keychain** under service name \`SarabiLabs_Uber_Automator\`. Keys: \`google_client_id\`, \`google_client_secret\`, \`gmail_app_password\`, \`twilio_sid\`, \`twilio_token\`, \`twilio_phone\`, \`son_phone\`, \`uber_server_token\`, \`home_address\`. Seed them with \`make seed-secrets\`. Never store secrets in \`.env\` or code.

Google OAuth tokens are written to disk by \`scripts/auth_setup.py\` (one-time browser flow). The worker reads them at startup via \`skills/gmail_auth/handler.py\`.

## Skill Orchestration Sequence

`local_worker.py` calls skills in this order per email:
1. `gmail_precheck` — verify IMAP reachable
2. IMAP fetch — get unread from `SON_EMAIL`
3. `email_parser` — extract ride time + address
4. `ride_scheduler` — validate 2:35/4PM slot (±10 min); reject otherwise
5. `rate_limiter.can_book()` — abort if today's count ≥ 2
6. `session_manager.refresh_needed()` — warn if session stale (no Playwright)
7. `ride_request` — book via Playwright (wrapped by `retry_agent`, 3 attempts)
8. `rate_limiter.record_booking()` — increment on confirmed success only
9. `notifier` — SMS + macOS alert
10. `email_reply` — send confirmation or failure email

## Subagents

| Agent | Purpose | When to use |
|-------|---------|-------------|
| `health_monitor.py` | launchd + session freshness + disk | ops diagnostics |
| `retry_agent.py` | exponential backoff (5s, 10s, 20s, cap 60s) | wraps `ride_request` |
| `session_agent.py` | file-level session age/state (no browser) | fast pre-flight check |

## MCP Plugin (scripts/mcp_server.py)

Exposes 4 tools callable from Claude Code:
- `check_uber_session` — valid/expired + reason
- `get_ride_count_today` — N/2 for today
- `check_launchd_service` — running/stopped
- `get_agent_logs(lines)` — tail stdout.log

Install mcp separately (`pip install mcp`) — incompatible with project's pydantic==2.7.1.

## Conventions

- `skills/` are stateless, independently testable units. No polling logic inside them.
- `agents/local_worker.py` owns the loop, IMAP connection, and skill orchestration.
- Use `imaplib` for Gmail (IMAP/IDLE), `playwright` for Uber browser automation, `twilio` for SMS.
- No boto3 or AWS SDK — this is a local-first project.
- Logs go to `logs/stdout.log` and `logs/stderr.log` (managed by launchd).
- Hook events logged to `logs/hook.log` (Claude Code PostToolUse/Stop hooks).

## Key Config

- Poll interval: 300s (5 min) — defined in `agents/local_worker.py`
- Pickup coords: resolved dynamically via Nominatim geocoder from `SCHOOL_ADDRESS = "855 Grove Ave, Edison, NJ 08820"` in `ride_request/handler.py` + `core/geocoder.py`
- Sender filter: `SON_EMAIL` — defined in `core/settings.py`
- Rate limit: 2 rides/day — state in `config/ride_count.json`, enforced by `skills/rate_limiter/handler.py`
- Allowed slots: 2:35 PM and 4:00 PM EST ±10 min — enforced by `skills/ride_scheduler/handler.py`
- Session max age: 7 days — checked by `session_manager`, `session_agent`, `health_monitor`