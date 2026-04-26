import os
import requests
import time

# =========================
# CONFIG
# =========================

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
HF_TOKEN = os.getenv("HF_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
} if HF_TOKEN else {}

CACHE = {}


# =========================
# AI CALL FUNCTION
# =========================

def call_ai(prompt, retries=3):
    for attempt in range(retries):
        try:
            response = requests.post(
                API_URL,
                headers=HEADERS,
                json={"inputs": prompt},
                timeout=60
            )

            # Model loading
            if response.status_code == 503:
                time.sleep(2)
                continue

            if response.status_code != 200:
                return None

            data = response.json()

            # Handle response format safely
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("generated_text", "").strip()

            if isinstance(data, dict):
                return data.get("generated_text", "").strip()

            return None

        except Exception:
            time.sleep(2)

    return None


# =========================
# FALLBACK EXPLANATION
# =========================

def fallback(rule_id, message):
    return f"""
Explanation:
{message}

Why dangerous:
Attackers can exploit this vulnerability to gain unauthorized access or manipulate system behavior.

Hacker perspective:
An attacker can use {rule_id} to inject malicious input or execute unintended actions.

Fix:
Use secure coding practices and validate all inputs properly.
""".strip()


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
        prompt = f"""
You are a cybersecurity expert.

Explain the following vulnerability in a very simple and clear way.

Vulnerability: {rule_id}
Details: {message}

Give output in this format:

Explanation:
(simple explanation)

Why dangerous:
(real-world impact)

Hacker perspective:
(how attacker exploits it)

Fix:
(secure solution with example if possible)
"""

        if HF_TOKEN:
            ai_output = call_ai(prompt)
            if not ai_output:
                ai_output = fallback(rule_id, message)
        else:
            ai_output = fallback(rule_id, message)

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