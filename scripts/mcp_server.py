"""
MCP server exposing Uber agent status tools to Claude.
Run: uv run python scripts/mcp_server.py

Requires: pip install mcp  (separate from main venv due to pydantic constraint)
"""
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def check_uber_session() -> str:
    state_file = PROJECT_ROOT / "config" / "uber_state.json"
    if not state_file.exists():
        return "expired: missing"
    age_days = (datetime.now().timestamp() - os.stat(state_file).st_mtime) / 86400
    if age_days >= 7:
        return f"expired: age: {age_days:.1f} days"
    return "valid"


def get_ride_count_today() -> str:
    count_file = PROJECT_ROOT / "config" / "ride_count.json"
    if not count_file.exists():
        return "count: 0/2 (no state)"
    try:
        data = json.loads(count_file.read_text())
        return f"count: {data.get('count', 0)}/2 for {data.get('date', 'unknown')}"
    except (json.JSONDecodeError, OSError):
        return "count: 0/2 (no state)"


def check_launchd_service() -> str:
    result = subprocess.run(
        ["launchctl", "list", "com.sarabilabs.rideagent"],
        capture_output=True, text=True,
    )
    if result.returncode == 0 and "PID" in result.stdout:
        return "running"
    return f"stopped: {result.stderr.strip()}"


def get_agent_logs(lines: int = 20) -> str:
    log_file = PROJECT_ROOT / "logs" / "stdout.log"
    if not log_file.exists():
        return "no logs"
    all_lines = log_file.read_text().splitlines()
    return "\n".join(all_lines[-lines:])


if __name__ == "__main__":
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("SarabiLabs Uber Agent")
    mcp.tool()(check_uber_session)
    mcp.tool()(get_ride_count_today)
    mcp.tool()(check_launchd_service)
    mcp.tool()(get_agent_logs)
    mcp.run()
