import os
import requests
import time

# =========================
# CONFIG
# =========================

# Keep same model (as in your report)
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

        # Model loading case
        if response.status_code == 503:
            print("⏳ Model loading... retrying")
            time.sleep(3)
            return call_ai(prompt)

        # Debug for checking API
        print(f"[DEBUG] Status: {response.status_code}")

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
This vulnerability is related to {message}. It is an insecure coding practice that may expose the application to attackers.

Why dangerous:
Attackers can use this weakness to access sensitive information, execute malicious code, or compromise the system.

Hacker perspective:
Hackers actively search for {rule_id} vulnerabilities because they provide easy entry points into applications.

Fix:
Use secure coding practices, validate inputs properly, avoid unsafe functions, and protect sensitive data using secure methods.
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

        # STRONG PROMPT ENGINEERING
        prompt = f"""
You are a senior cybersecurity expert helping beginner students understand software vulnerabilities.

Your task is to explain the vulnerability clearly and uniquely.

STRICT RULES:
1. Do NOT simply repeat the vulnerability name
2. Explain the real meaning of the vulnerability
3. Use beginner-friendly simple English
4. Explain why it is dangerous in real life
5. Explain how hackers misuse it
6. Explain the exact secure fix
7. Each vulnerability must have a DIFFERENT explanation
8. Response must be practical and student-friendly

EXAMPLE:

Vulnerability: HARDCODED_PASSWORD

Explanation:
A hardcoded password means the password is directly written inside the source code instead of storing it securely using environment variables or secret managers.

Why dangerous:
If someone gets access to the source code, they can easily see the password and use it to access databases, admin panels, or servers.

Hacker perspective:
Hackers often scan GitHub repositories searching for exposed passwords. Once found, they can log in directly without needing advanced attacks.

Fix:
Store passwords using environment variables or secret management systems instead of writing them directly inside the code.


NOW EXPLAIN THIS:

Vulnerability: {rule_id}
Details: {message}

Return ONLY in this exact format:

Explanation:
Why dangerous:
Hacker perspective:
Fix:
"""

        # AI or fallback
        if HF_TOKEN:
            ai_output = call_ai(prompt)

            if not ai_output:
                print("⚠ Using fallback response")
                ai_output = fallback(rule_id, message)
        else:
            print("⚠ HF_TOKEN missing → using fallback")
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