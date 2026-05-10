# Projected

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
│   └── config/
│       └── uber_state.json
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
├── Docs / Architecture
│   ├── README.md
│   ├── CLAUDE.md
│   ├── CLAUDE.template.md
│   ├── architecture.mmd
│   ├── DevOps.mmd
│   ├── SAMPLE_EMAIL.md
│   └── FILES.md
│
└── Runtime state
    └── config/uber_state.json

# Actual Shortlist

uber-agent-automation-local/
│
├── .claude
│   └── settings.local.json
├── .env
├── agents
│   ├── __pycache__
│   └── local_worker.py
├── config
│   └── uber_state.json
├── logs
│   ├── stderr.log
│   └── stdout.log
├── pyproject.toml
├── requirements.txt
├── scripts
│   ├── __pycache__
│   ├── auth_setup.py
│   ├── check_session.py
│   ├── uber_login.py
│   └── use_uber_session.py
├── skills
│   ├── email_parser
│   ├── email_reply
│   ├── gmail_auth
│   ├── notifier
│   └── ride_request
└── uv.lock

# Actual

uber-agent-automation-local/
│
├── .DS_Store
├── .aider.chat.history.md
├── .aider.input.history
├── .aider.model.metadata.json
├── .aider.tags.cache.v4
│   └── cache.db
├── .claude
│   └── settings.local.json
├── .env
├── .git
│   ├── COMMIT_EDITMSG
│   ├── FETCH_HEAD
│   ├── HEAD
│   ├── ORIG_HEAD
│   ├── config
│   ├── description
│   ├── filter-repo
│   ├── gk
│   ├── hooks
│   ├── index
│   ├── info
│   ├── logs
│   ├── objects
│   ├── packed-refs
│   └── refs
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── .venv
│   ├── .gitignore
│   ├── .lock
│   ├── CACHEDIR.TAG
│   ├── bin
│   ├── include
│   ├── lib
│   └── pyvenv.cfg
├── .vscode
│   └── commander.json
├── CLAUDE.md
├── CLAUDE.template.md
├── DevOps.mmd
├── FILES.md
├── LAUNCHD_6yr_Guide.pdf
├── Makefile
├── Modelfile
├── README.md
├── SAMPLE_EMAIL.md
├── Using launchctl and launchd.md
├── agents
│   ├── __pycache__
│   └── local_worker.py
├── architecture.mmd
├── auth
├── client_secrets.json
├── com.sarabilabs.rideagent.plist
├── config
│   └── uber_state.json
├── folders.txt
├── logs
│   ├── stderr.log
│   └── stdout.log
├── pyproject.toml
├── requirements.txt
├── scripts
│   ├── __pycache__
│   ├── auth_setup.py
│   ├── check_session.py
│   ├── uber_login.py
│   └── use_uber_session.py
├── skills
│   ├── email_parser
│   ├── email_reply
│   ├── gmail_auth
│   ├── notifier
│   └── ride_request
└── uv.lock

29 directories, 48 files
