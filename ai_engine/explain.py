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
# STATIC KNOWLEDGE BASE
# =========================

RULE_EXPLANATIONS = {
    "HARDCODED_PASSWORD": {
        "explanation": "A password is directly written in the source code instead of secure storage.",
        "danger": "Attackers can easily find credentials and gain unauthorized access.",
        "hacker": "Attacker scans code and extracts password to log in without permission.",
        "fix": "Use environment variables or secure vaults."
    },

    "HARDCODED_SECRET": {
        "explanation": "Sensitive keys like API tokens are exposed in the code.",
        "danger": "Can lead to data leaks or unauthorized API usage.",
        "hacker": "Attacker steals API key and abuses backend services.",
        "fix": "Store secrets in environment variables."
    },

    "DANGEROUS_EVAL": {
        "explanation": "eval() executes dynamic code which is unsafe.",
        "danger": "Allows execution of attacker-controlled code.",
        "hacker": "Injected code runs on the system.",
        "fix": "Avoid eval() and use safe parsing methods."
    },

    "DANGEROUS_EXEC": {
        "explanation": "exec() executes arbitrary code.",
        "danger": "Can lead to full system compromise.",
        "hacker": "Attacker injects malicious code execution.",
        "fix": "Remove exec() or validate input strictly."
    },

    "COMMAND_INJECTION": {
        "explanation": "User input is passed into system commands.",
        "danger": "Allows execution of unauthorized system commands.",
        "hacker": "Attacker injects shell commands to control system.",
        "fix": "Use parameterized commands and sanitize input."
    },

    "UNSAFE_DESERIALIZATION": {
        "explanation": "Unsafe deserialization of data (like pickle).",
        "danger": "Can lead to remote code execution.",
        "hacker": "Attacker sends malicious serialized object.",
        "fix": "Avoid unsafe deserialization or validate input."
    },

    "DEBUG_MODE_ON": {
        "explanation": "Debug mode is enabled in production.",
        "danger": "Exposes sensitive internal system details.",
        "hacker": "Attacker uses debug info for exploitation.",
        "fix": "Disable debug mode in production."
    },

    "INSECURE_HTTP": {
        "explanation": "HTTP is used instead of HTTPS.",
        "danger": "Data can be intercepted in transit.",
        "hacker": "Man-in-the-middle attack steals data.",
        "fix": "Use HTTPS."
    },

    "HIDDEN_EXCEPTION": {
        "explanation": "Exceptions are silently ignored.",
        "danger": "Errors are hidden and security issues go unnoticed.",
        "hacker": "Attacker triggers silent failures.",
        "fix": "Log exceptions properly."
    },

    "WEAK_RANDOM_USAGE": {
        "explanation": "Weak random generator used for security purposes.",
        "danger": "Predictable outputs can be exploited.",
        "hacker": "Attacker predicts random values.",
        "fix": "Use cryptographically secure random functions."
    }
}

# =========================
# AI CALL FUNCTION
# =========================

def call_ai(prompt):
    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": prompt},
            timeout=60
        )

        print("HF STATUS:", response.status_code)
        print("HF RESPONSE:", response.text)

        data = response.json()

        if isinstance(data, dict) and "error" in data:
            return None

        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text")

        return None

    except Exception as e:
        print("AI ERROR:", str(e))
        return None


# =========================
# FALLBACK FUNCTION
# =========================

def fallback(rule_id, message):
    rule = RULE_EXPLANATIONS.get(rule_id)

    if rule:
        return f"""
Explanation: {rule['explanation']}

Why dangerous: {rule['danger']}

Hacker perspective: {rule['hacker']}

Fix: {rule['fix']}
"""
    else:
        return f"""
Explanation: {message}. This is a security issue in the code.

Why dangerous: It may lead to security vulnerabilities or system compromise.

Hacker perspective: Attackers may analyze and exploit this weakness.

Fix: Follow secure coding practices and validate inputs.
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

        prompt = f"""
You are a cybersecurity expert.

Explain this vulnerability clearly.

Vulnerability: {rule_id}
Details: {message}

Format:
Explanation:
Why dangerous:
Hacker perspective:
Fix:
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

🤖 Analysis:
{ai_output}

==============================
"""