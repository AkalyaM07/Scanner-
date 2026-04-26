import os
import requests
import time

# =========================
# CONFIG
# =========================

# Original working API URL
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

HF_TOKEN = os.getenv("HF_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
} if HF_TOKEN else {}

# Cache to avoid repeated API calls
CACHE = {}


# =========================
# AI CALL FUNCTION
# =========================

def call_ai(prompt):
    """
    Calls Hugging Face API safely
    """

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": prompt},
            timeout=60
        )

        print(f"[DEBUG] Status: {response.status_code}")

        # Model loading case
        if response.status_code == 503:
            print("⏳ Model loading... retrying...")
            time.sleep(3)
            return call_ai(prompt)

        # API failure → return None
        if response.status_code != 200:
            print(f"[DEBUG] Error: {response.text}")
            return None

        data = response.json()
        print(f"[DEBUG] Response: {data}")

        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "")

        if isinstance(data, dict):
            return data.get("generated_text", "")

        return None

    except Exception as e:
        print(f"[DEBUG] Exception: {e}")
        return None


# =========================
# FALLBACK EXPLANATION
# =========================

def fallback(rule_id, message):
    return f"""
Explanation:
This vulnerability is related to {message}. It represents an insecure coding practice that may expose the application to attackers.

Why dangerous:
Attackers can exploit this weakness to gain unauthorized access, steal sensitive data, execute malicious commands, or compromise the system.

Hacker perspective:
Hackers actively search for {rule_id} vulnerabilities because they often provide easy entry points into applications and servers.

Fix:
Use secure coding practices, validate all inputs properly, avoid unsafe functions, and protect sensitive information using secure methods.
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
        # Better prompt for unique explanations
        prompt = f"""
You are a cybersecurity expert helping beginner developers understand vulnerabilities.

Explain this vulnerability in simple student-friendly language.

IMPORTANT:
- Do NOT repeat only the vulnerability name
- Give unique explanation for this specific vulnerability
- Explain what it means clearly
- Explain why it is dangerous
- Explain how hackers can misuse it
- Explain how developers can fix it

Example:

Vulnerability: HARDCODED_PASSWORD

Explanation:
A hardcoded password means a password is directly written inside source code instead of being stored securely using environment variables or secret managers.

Why dangerous:
If someone gains access to the code, they can immediately see the password and use it to access databases, admin panels, or servers.

Hacker perspective:
Hackers search GitHub repositories for exposed passwords. Once found, they use them to break into systems without needing to hack further.

Fix:
Store passwords in environment variables or secure secret managers instead of writing them directly inside the code.


Now explain this vulnerability:

Vulnerability: {rule_id}
Details: {message}

Return ONLY in this format:

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

🤖 AI Analysis:
{ai_output}

==============================
"""