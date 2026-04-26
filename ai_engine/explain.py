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

def call_ai(prompt):
    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 300,
                    "temperature": 0.3,
                    "return_full_text": False
                }
            },
            timeout=60
        )

        # Model loading
        if response.status_code == 503:
            print("⏳ Model loading... retrying")
            time.sleep(3)
            return call_ai(prompt)

        if response.status_code != 200:
            print(f"⚠ API Error: {response.status_code}")
            return None

        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "")

        if isinstance(data, dict):
            return data.get("generated_text", "")

        return None

    except Exception as e:
        print(f"⚠ API Exception: {e}")
        return None


# =========================
# GENERIC FALLBACK
# =========================

def fallback(rule_id):
    return f"""
Explanation:
This vulnerability represents an insecure coding practice that may expose the application to attackers.

Why Dangerous:
Attackers may use this weakness to access sensitive data, execute malicious actions, or compromise the system.

Hacker Perspective:
Hackers actively search for {rule_id} type vulnerabilities because they often provide an easy entry point into applications.

Fix:
Follow secure coding standards, validate all inputs, avoid unsafe functions, and securely handle sensitive data.
"""


# =========================
# PROMPT ENGINEERING
# =========================

def build_prompt(rule_id, message):
    return f"""
You are a cybersecurity expert helping beginner developers understand security vulnerabilities.

IMPORTANT RULES:
- Give UNIQUE answers for each vulnerability
- Do NOT repeat the same answer for all vulnerabilities
- Do NOT just repeat the vulnerability name
- Explain the exact meaning of this vulnerability
- Answer in simple student-friendly English
- Give practical hacker perspective

EXAMPLE 1:

Vulnerability: HARDCODED_PASSWORD

Explanation:
A hardcoded password means the password is directly written inside the source code instead of storing it securely outside the code.

Why Dangerous:
If someone gets access to the code, they can easily see the password and use it to access the system without permission.

Hacker Perspective:
Hackers search GitHub repositories for exposed passwords. If they find one, they can use it to log in to admin panels, databases, or servers.

Fix:
Store passwords in environment variables or secret managers instead of writing them directly inside code.


EXAMPLE 2:

Vulnerability: DANGEROUS_EVAL

Explanation:
Using eval() allows Python to execute input as code. If user input is passed into eval(), attackers can run harmful commands.

Why Dangerous:
This can lead to remote code execution where attackers run malicious code on the server.

Hacker Perspective:
Hackers may inject malicious Python commands through user input and take full control of the application.

Fix:
Avoid using eval(). Use safer alternatives like ast.literal_eval() or proper input validation.


NOW EXPLAIN THIS:

Vulnerability: {rule_id}
Detected Message: {message}

Return ONLY in this format:

Explanation:
Why Dangerous:
Hacker Perspective:
Fix:
"""


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
        prompt = build_prompt(rule_id, message)

        if HF_TOKEN:
            ai_output = call_ai(prompt)

            # weak response check
            if (
                not ai_output
                or len(ai_output.strip()) < 40
                or ai_output.strip().lower() == rule_id.lower()
                or "Explanation: Hardcoded Password" in ai_output
            ):
                print("⚠ Weak AI response detected → using fallback")
                ai_output = fallback(rule_id)

        else:
            print("⚠ HF_TOKEN missing → using fallback")
            ai_output = fallback(rule_id)

        CACHE[cache_key] = ai_output

    return f"""
==============================

🔴 Issue: {rule_id}
📄 File: {path} (Line {line})

⚠️ Message:
{message}

🤖 AI Explanation:
{ai_output}

==============================
"""