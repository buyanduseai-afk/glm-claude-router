# GLM Claude Router

A Claude Code skill that routes user prompts through a GLM-based classifier. Simple prompts are answered by GLM directly; complex or errored prompts fall back to native Claude capabilities.

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                      User Prompt                        │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│            GLM Claude Router (SKILL.md)                  │
│                                                          │
│  1. Write prompt to temp file (safe heredoc — zero       │
│     shell expansion, handles all special characters)     │
│  2. Pipe to router.py                                    │
│  3. router.py calls ZAI/GLM API for classification       │
│  4. Returns JSON: {"status": "...", "message": "..."}    │
└──────────────────────────┬──────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │  Parse JSON │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
      ┌──────────┐  ┌───────────┐  ┌───────────┐
      │ "simple" │  │ "complex" │  │  "error"  │
      └────┬─────┘  └─────┬─────┘  └─────┬─────┘
           │              │              │
           ▼              ▼              ▼
      ┌──────────┐  ┌───────────┐  ┌───────────┐
      │  Output  │  │ Use full  │  │ Use full  │
      │  GLM's   │  │  native   │  │  native   │
      │ message  │  │  Claude   │  │  Claude   │
      │ verbatim │  │           │  │           │
      └──────────┘  └───────────┘  └───────────┘
```

## Quick Install

```bash
bash install.sh
```

## Manual Installation

If you prefer to install manually:

1. Download the ZIP and extract it.
2. Copy `SKILL.md` and `router.py` to your Claude skills directory:

```bash
mkdir -p ~/.claude/skills/glm-claude-router
cp SKILL.md router.py ~/.claude/skills/glm-claude-router/
chmod +x ~/.claude/skills/glm-claude-router/router.py
```

3. Install the Python dependency:

```bash
python3 -m pip install --user requests
```

4. Add your API key to `~/.claude/settings.json`:

```json
{
  "env": {
    "ZAI_API_KEY": "your-api-key-here"
  }
}
```

5. Restart Claude Code.

## Troubleshooting

- **ZAI_API_KEY is not set**: Re-run `install.sh` or manually edit `~/.claude/settings.json`.
- **ModuleNotFoundError: No module named 'requests'**: Run `python3 -m pip install --user requests`.
- **Router always returns "complex"**: Check your internet connection and API key validity.

## License

MIT
