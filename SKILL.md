---
name: glm-claude-router
description: Routes user prompts through a GLM-based classifier. Simple prompts are answered by GLM and output verbatim; complex or errored prompts fall back to native Claude capabilities.
---

# GLM Claude Router

This skill intercepts every user prompt, classifies its complexity via the ZAI/GLM API, and routes accordingly:

- **simple** → Output GLM's `message` field exactly as-is. No preamble, no postscript, no formatting changes.
- **complex** → Ignore the router output entirely. Answer the user's original prompt using your full native Claude capabilities.
- **error** → Ignore the router output entirely. Answer the user's original prompt using your full native Claude capabilities.

## Execution

When a user sends a prompt, you MUST execute the bash command below before responding.

### Bash Command

```bash
_ROUTER_TMP=$(mktemp) && cat > "$_ROUTER_TMP" << 'GLMROUTEREOF'
[INSERT USER PROMPT VERBATIM HERE]
GLMROUTEREOF
python3 ~/.claude/skills/glm-claude-router/router.py < "$_ROUTER_TMP"; rm -f "$_ROUTER_TMP"
```

> Replace `[INSERT USER PROMPT VERBATIM HERE]` with the user's exact message.
> The single-quoted heredoc delimiter (`'GLMROUTEREOF'`) prevents all shell expansion,
> making this safe for prompts containing backticks, dollar signs, and other special characters.

### Parsing the Output

The router outputs a single JSON line to stdout:

```json
{"status": "simple", "message": "The complete response to show the user."}
```

## Routing Decision Table

| `status` value | Action |
|---|---|
| `"simple"` | Output the `"message"` field **exactly as-is** to the user. Do not add any of your own thoughts. |
| `"complex"` | Discard the router output completely. Answer the user's original prompt yourself using native Claude. |
| `"error"` | Discard the router output completely. Answer the user's original prompt yourself using native Claude. |

## Fallback Rules

If any of the following occur, treat it as `"complex"` and answer natively:

- The bash command produces no stdout
- The stdout is not valid JSON
- The JSON lacks a `"status"` field
- The command times out or hangs

When in doubt, fall back to native Claude. Never leave the user without an answer.
