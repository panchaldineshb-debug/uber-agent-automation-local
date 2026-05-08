.PHONY: help install local-dev setup load unload reload status clean 
.PHONY: uber-login uber-run uber-persistent
.PHONY: check check-twilio check-launchctl
.PHONY: seed-secrets
.PHONY: test
.PHONY: logs

# Python environment and paths
VENV := .venv
PYTHON=python3
PIP := pip3

# Modern launchd domain
SERVICE_NAME=com.sarabilabs.rideagent
PLIST_FILENAME=$(SERVICE_NAME).plist
PLIST_DEST=$(HOME)/Library/LaunchAgents/$(PLIST_FILENAME)

# Logs
WORKER=agents/local_worker.py
LOG_DIR=logs

# Modern launchd domain
USER_ID=$(shell id -u)
DOMAIN=gui/$(USER_ID)

# UV Path Detection
UV_PYTHON=$(shell uv run which python)


AUTH_FILE := auth/uber_state.json

.DEFAULT_GOAL := help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install Python deps via uv
	uv sync

setup: ## Generate the launchd plist using the UV virtualenv path
	@mkdir -p $(LOG_DIR)
	@echo "Generating $(PLIST_FILENAME)..."
	@printf '<?xml version="1.0" encoding="UTF-8"?>\n\
	<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n\
	<plist version="1.0">\n\
	<dict>\n\
		<key>Label</key>\n\
		<string>$(SERVICE_NAME)</string>\n\
		<key>ProgramArguments</key>\n\
		<array>\n\
			<string>$(UV_PYTHON)</string>\n\
			<string>$(CURDIR)/$(WORKER)</string>\n\
		</array>\n\
		<key>RunAtLoad</key>\n\
		<true/>\n\
		<key>KeepAlive</key>\n\
		<true/>\n\
		<key>WorkingDirectory</key>\n\
		<string>$(CURDIR)</string>\n\
		<key>StandardOutPath</key>\n\
		<string>$(CURDIR)/$(LOG_DIR)/stdout.log</string>\n\
		<key>StandardErrorPath</key>\n\
		<string>$(CURDIR)/$(LOG_DIR)/stderr.log</string>\n\
		<key>EnvironmentVariables</key>\n\
		<dict>\n\
			<key>PYTHONUNBUFFERED</key>\n\
			<string>1</string>\n\
			<key>PYTHONPATH</key>\n\
			<string>$(CURDIR)</string>\n\
		</dict>\n\
	</dict>\n\
	</plist>\n' > $(PLIST_DEST)
	@plutil -lint $(PLIST_DEST)
	@echo "✅ Done. Run 'make load' to install."

auth: ## Re-run Google OAuth (deletes token.json first)
	uv run python scripts/auth_setup.py

load: ## Bootstrap the service into the user domain
	cp $(PLIST_FILENAME) $(PLIST_DEST)
	launchctl bootstrap $(DOMAIN) $(PLIST_DEST)
	@echo "🚀 Service bootstrapped into $(DOMAIN)."

local-dev: ## Launch Claude Code using local Qwen2.5-Coder via Ollama
	@echo "🤖 Starting local dev session with qwen2.5-coder:7b..."
	@ollama list | grep -q "qwen2.5-coder:7b" || ollama pull qwen2.5-coder:7b
	ollama launch claude --model qwen2.5-coder:7b

unload: ## Bootout/Stop the service
	launchctl bootout $(DOMAIN) $(PLIST_DEST) 2>/dev/null || true
	@echo "🛑 Service bootout complete."

reload: unload setup load ## Full cycle: Unload, regenerate config, and restart
	@launchctl kickstart -p $(DOMAIN)/$(SERVICE_NAME)
	@echo "🔄 Service reloaded with latest config and code"

status: ## Check if the service is running
	launchctl list | grep $(SERVICE_NAME) || echo "Service not running."

seed-secrets: ## Interactively set Google, Twilio, and Contact secrets
	@read -p "Enter Google Client ID: " g_id; \
	read -p "Enter Google Client Secret: " g_secret; \
	read -p "Enter Gmail App Password: " g_app_pass; \
	read -p "Enter Twilio SID: " t_sid; \
	read -p "Enter Twilio Auth Token: " t_token; \
	read -p "Enter Twilio Phone Number: " t_phone; \
	read -p "Enter Sameer's Phone Number: " s_phone; \
	uv run python -c "\
import keyring; s='SarabiLabs_Uber_Automator'; \
pairs = [('google_client_id','$$g_id'),('google_client_secret','$$g_secret'),('gmail_app_password','$$g_app_pass'),('twilio_sid','$$t_sid'),('twilio_token','$$t_token'),('twilio_phone','$$t_phone'),('son_phone','$$s_phone')]; \
[keyring.set_password(s,k,v) for k,v in pairs if v.strip()]; \
print('Secrets updated (blank entries skipped).')"; \

check: ## Compact Keychain credential verification
	@uv run python -c "import keyring; s='SarabiLabs_Uber_Automator'; \
	print('Keychain Status:', {k: '✅' for k in ['google_client_id', 'google_client_secret', 'google_refresh_token', 'twilio_sid', 'twilio_token', 'twilio_phone', 'son_phone'] if keyring.get_password(s, k)})"

check-twilio: ## Print Twilio secrets from Keychain (masked)
	uv run python3 -c "\
import keyring; s='SarabiLabs_Uber_Automator'; \
print('twilio_sid:', repr(keyring.get_password(s, 'twilio_sid'))); \
print('twilio_token:', repr(keyring.get_password(s, 'twilio_token'))); \
print('twilio_phone:', repr(keyring.get_password(s, 'twilio_phone')))"

check-launchctl: ## Dry run of the launchd configuration
	@echo "🔍 Testing plist syntax..."
	@plutil -lint $(PLIST_FILENAME)
	@echo "🔍 Testing path existence..."
	@ls $(UV_PYTHON) > /dev/null && echo "✅ Python path valid"
	@ls $(CURDIR)/$(WORKER) > /dev/null && echo "✅ Worker script valid"

check-session:
	@echo "🔍 Testing plist syntax..."
	@plutil -lint $(PLIST_FILENAME)
	@echo "🔍 Testing Uber session validity..."
	uv run python scripts/check_session.py

# =========================
# Uber Authentication
# =========================

uber-login:
	uv run python  scripts/uber_login.py

uber-run:
	uv run python  scripts/use_uber_session.py

uber-persistent:
	uv run python  scripts/persistent_profile.py


# =========================
# Logs
# =========================
logs: ## Tail the service logs
	tail $(LOG_DIR)/stdout.log

test: ## Run pytest suite
	$(PYTHON) -m pytest tests/

clean: unload ## Remove logs and local plist
	rm -rf $(LOG_DIR)/*.log
	rm -f $(PLIST_FILENAME)
	@echo "🧹 Cleaned local artifacts"