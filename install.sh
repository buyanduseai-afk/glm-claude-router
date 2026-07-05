#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

echo -e "${BOLD}GLM Claude Router — Automated Installer${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_HOME="${HOME}/.claude"
SKILLS_DIR="${CLAUDE_HOME}/skills"
TARGET_DIR="${SKILLS_DIR}/glm-claude-router"
SETTINGS_FILE="${CLAUDE_HOME}/settings.json"

info "Checking for Python 3..."
if command -v python3 &>/dev/null; then
    ok "Python 3 found."
else
    error "Python 3 is not installed. Please install it first."
    exit 1
fi

info "Checking for 'requests' library..."
if python3 -c "import requests" 2>/dev/null; then
    ok "requests is installed."
else
    warn "'requests' not found. Installing..."
    python3 -m pip install --user requests || python3 -m pip install requests
fi

info "Installing skill to: ${TARGET_DIR}"
mkdir -p "${SKILLS_DIR}"
rm -rf "${TARGET_DIR}"
mkdir -p "${TARGET_DIR}"
cp "${SCRIPT_DIR}/SKILL.md" "${TARGET_DIR}/SKILL.md"
cp "${SCRIPT_DIR}/router.py" "${TARGET_DIR}/router.py"
chmod +x "${TARGET_DIR}/router.py"
ok "Files copied."

echo ""
read -rsp "$(echo -e "${BOLD}Enter your ZAI API key:${NC} ")" API_KEY
echo ""

if [[ -z "${API_KEY}" ]]; then
    warn "No API key provided. You can add it manually later to ${SETTINGS_FILE}."
    exit 0
fi

info "Configuring ${SETTINGS_FILE}..."
python3 - "$SETTINGS_FILE" "$API_KEY" << 'PYTHON_EOF'
import json, os, sys
settings_path, api_key = sys.argv[1], sys.argv[2]
settings = {}
if os.path.exists(settings_path):
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.loads(f.read().strip())
    except Exception:
        pass
if not isinstance(settings, dict):
    settings = {}
if "env" not in settings or not isinstance(settings["env"], dict):
    settings["env"] = {}
settings["env"]["ZAI_API_KEY"] = api_key
with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("OK")
PYTHON_EOF

ok "ZAI_API_KEY injected successfully."
echo -e "${GREEN}${BOLD}Installation Complete!${NC}"
echo -e "Restart Claude Code to activate the skill."
