#!/usr/bin/env python3
import json
import os
import sys
import time
import requests

API_URL = "https://api.z.ai/api/paas/v4/chat/completions"
MODEL = "glm-4-flash"
TIMEOUT = 30
MAX_RETRIES = 2
RETRY_DELAY = 1.0

CLASSIFICATION_SYSTEM = (
    "You are a prompt classification router. Analyze the user's prompt and "
    "classify it into exactly one of three categories:\n\n"
    "1. \"simple\" — The prompt is straightforward: basic facts, greetings, "
    "simple lookups, formatting tasks, or standard questions that need no "
    "multi-step reasoning, code generation, or specialized expertise.\n\n"
    "2. \"complex\" — The prompt requires deep reasoning, multi-step analysis, "
    "code generation, creative writing, mathematical problem-solving, "
    "architectural design, or specialized expertise.\n\n"
    "3. \"error\" — The prompt is empty, unclear, or potentially harmful.\n\n"
    "Respond with ONLY a valid JSON object on a single line:\n"
    "{\"status\": \"simple\", \"message\": \"<complete helpful response>\"}\n"
    "For \"simple\" status, the message MUST be a complete, ready-to-deliver "
    "response. For \"complex\" and \"error\", provide a brief explanation. "
    "Output JSON only — no markdown, no code fences, no extra text."
)


def output(status: str, message: str) -> None:
    print(json.dumps({"status": status, "message": message}, ensure_ascii=False))
    sys.exit(0)


def extract_json(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        json_lines = []
        in_block = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_block = not in_block
                continue
            if in_block:
                json_lines.append(line)
        content = "\n".join(json_lines).strip()

    if not content.startswith("{"):
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            content = content[start : end + 1]
    return content


def main() -> None:
    try:
        prompt = sys.stdin.read()
    except Exception as e:
        output("error", f"Failed to read input: {e}")
        return

    if not prompt or not prompt.strip():
        output("error", "Empty prompt received.")
        return

    api_key = os.environ.get("ZAI_API_KEY", "").strip()
    if not api_key:
        output("error", "ZAI_API_KEY is not set.")
        return

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": CLASSIFICATION_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(API_URL, json=payload, headers=headers, timeout=TIMEOUT)
            resp.raise_for_status()
            result = resp.json()
            content = result["choices"][0]["message"]["content"].strip()

            json_str = extract_json(content)
            parsed = json.loads(json_str)

            status = parsed.get("status", "")
            if status not in ("simple", "complex", "error"):
                raise ValueError(f"Invalid status value: {status!r}")

            message = parsed.get("message", "")
            if not message and status == "simple":
                output("complex", "Router returned empty message for simple status.")
                return

            output(status, message)
            return

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else "unknown"
            err_body = e.response.text[:500] if e.response is not None else ""
            last_error = f"HTTP {status_code}: {err_body}"
            if status_code == 429 and attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            elif isinstance(status_code, int) and 400 <= status_code < 500:
                output("error", f"API client error ({status_code})")
                return

        except requests.exceptions.RequestException:
            last_error = "Network error."
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue

        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            output("complex", f"Router classification parse error: {e}")
            return

        except Exception as e:
            last_error = f"Unexpected error: {e}"
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue

    output("error", f"API failed after retries. Last error: {last_error}")


if __name__ == "__main__":
    main()
