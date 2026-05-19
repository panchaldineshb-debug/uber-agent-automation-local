## Orchestrator Layer

`local_worker.py` owns the poll loop, IMAP/IDLE connection, and skill orchestration.

## Execution Sequence
1. `gmail_precheck` — verify IMAP reachable
2. IMAP fetch — get unread emails from `SON_EMAIL`
3. `email_parser` — extract ride time + address
4. `rate_limiter` — check max 2 rides/day; abort if exceeded
5. `session_manager` / `check_uber_health()` — verify Playwright session valid
6. `ride_request` — book via Playwright (wrapped by `retry_agent` for resilience)
7. `notifier` — SMS + macOS alert
8. `email_reply` — send confirmation or failure email

## Subagents Available
- `health_monitor.py` — check launchd, session freshness, disk space
- `retry_agent.py` — wrap any callable with exponential-backoff retry
- `session_agent.py` — file-level Uber session checks (no Playwright)

## Rules
- No polling logic inside skills — loop lives here only.
- Call `rate_limiter.can_book()` before every booking attempt.
- Call `rate_limiter.record_booking()` only on confirmed success.
- Poll interval: 300s defined in this file.
- Max rides/day: 2 (enforced by `skills/rate_limiter/handler.py`).
- WhatsApp trigger: planned, not implemented.
