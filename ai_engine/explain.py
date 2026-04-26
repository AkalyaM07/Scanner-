import os
import requests
import time

# =========================
# CONFIG
# =========================

API_URL = "https://router.huggingface.co/hf-inference/models/google/flan-t5-large/v1/chat/completions"
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("⚠️  WARNING: HF_TOKEN not set.")

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

CACHE = {}


# =========================
# AI CALL FUNCTION
# =========================

def call_ai(prompt):
    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={
                "model": "google/flan-t5-large",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 300
            },
            timeout=60
        )

        print(f"[DEBUG] Status: {response.status_code}")

        if response.status_code == 503:
            time.sleep(5)
            return call_ai(prompt)

        if response.status_code != 200:
            print(f"[DEBUG] Error: {response.text}")
            return "AI explanation unavailable."

        data = response.json()
        print(f"[DEBUG] Response: {data}")

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"[DEBUG] Exception: {e}")
        return "AI explanation unavailable."


# =========================
# MAIN FUNCTION
# =========================

def explain_issue(issue):
    rule_id = issue.get("check_id", "Unknown")
    path = issue.get("path", "Unknown file")
    line = issue.get("start", {}).get("line", "N/A")
    message = issue.get("extra", {}).get("message", "No details")

    cache_key = f"{rule_id}_{path}_{line}"

    if cache_key in CACHE:
        ai_output = CACHE[cache_key]
    else:
        prompt = f"""Explain this security vulnerability for a beginner developer.

Vulnerability: {rule_id}
Details: {message}

Explain: what it means, why it is dangerous, how a hacker exploits it, and how to fix it."""

        ai_output = call_ai(prompt)
        CACHE[cache_key] = ai_output

    return f"""
==============================

🔴 Issue: {rule_id}
📄 File: {path} (Line {line})

⚠️ Detected Message:
{message}

🤖 AI Analysis:
{ai_output}

==============================
"""