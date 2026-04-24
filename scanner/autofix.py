import os
import requests
import time
from datetime import datetime

# =========================
# AI CONFIG
# =========================
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
HF_TOKEN = os.getenv("HF_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
} if HF_TOKEN else {}


# =========================
# AI CALL
# =========================
def call_ai(prompt):
    try:
        res = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt}, timeout=60)

        if res.status_code == 503:
            time.sleep(3)
            return call_ai(prompt)

        if res.status_code != 200:
            return None

        data = res.json()

        if isinstance(data, list):
            return data[0].get("generated_text", "")

        return data.get("generated_text", "")

    except:
        return None


# =========================
# EXTRACT ONLY RELEVANT LINE
# =========================
def get_code_snippet(path, keyword):
    try:
        with open(path, "r", errors="ignore") as f:
            lines = f.readlines()

        for line in lines:
            if keyword.lower() in line.lower():
                return line.strip()

        return "Relevant code not found"

    except:
        return "Could not read file"


# =========================
# RULE-BASED FIXES (CORRECT)
# =========================
def rule_based_fix(issue):

    FIXES = {
        "HARDCODED_PASSWORD": "import os\npassword = os.getenv('PASSWORD')",

        "HARDCODED_SECRET": "import os\napi_key = os.getenv('API_KEY')",

        "DANGEROUS_EVAL": "import ast\nresult = ast.literal_eval(user_input)",

        "DANGEROUS_EXEC": "# Avoid exec()\n# Use safe function mapping instead",

        "SQL_INJECTION_RISK": "cursor.execute('SELECT * FROM users WHERE id=%s', (user_id,))",

        "COMMAND_INJECTION": "import subprocess\nsubprocess.run(['ls', '-l'])",

        "UNSAFE_SUBPROCESS": "subprocess.run(['command'], shell=False)",

        "UNSAFE_DESERIALIZATION": "import json\ndata = json.load(file)",

        "DEBUG_MODE_ON": "app.run(debug=False)",

        "INSECURE_HTTP": "Use https:// instead of http://",

        "HIDDEN_EXCEPTION": "except Exception as e:\n    print(e)",

        "WEAK_RANDOM_USAGE": "import secrets\nsecrets.token_hex()"
    }

    return FIXES.get(issue, None)


# =========================
# MAIN FUNCTION
# =========================
def generate_autofix(vulnerabilities):

    os.makedirs("reports", exist_ok=True)
    pdf_path = "reports/autofix_report.pdf"

    suggestions = []

    # keyword mapping to extract correct line
    keyword_map = {
        "HARDCODED_PASSWORD": "password",
        "HARDCODED_SECRET": "key",
        "DANGEROUS_EVAL": "eval(",
        "DANGEROUS_EXEC": "exec(",
        "SQL_INJECTION_RISK": "execute",
        "COMMAND_INJECTION": "os.system",
        "UNSAFE_SUBPROCESS": "subprocess",
        "UNSAFE_DESERIALIZATION": "pickle",
        "DEBUG_MODE_ON": "debug",
        "INSECURE_HTTP": "http://",
        "HIDDEN_EXCEPTION": "except",
        "WEAK_RANDOM_USAGE": "random"
    }

    for v in vulnerabilities:

        issue = v.get("check_id")
        path = v.get("path")
        message = v.get("extra", {}).get("message", "")

        keyword = keyword_map.get(issue, "")
        original_code = get_code_snippet(path, keyword)

        # =========================
        # RULE FIX FIRST
        # =========================
        fixed_code = rule_based_fix(issue)

        confidence = "High (Rule-based)"

        # =========================
        # AI FIX IF NO RULE
        # =========================
        if not fixed_code:
            prompt = f"""
Fix the security issue in this Python code.

Issue: {issue}
Problem: {message}

Code:
{original_code}

Return only fixed code.
"""

            ai_fix = call_ai(prompt)

            if ai_fix:
                fixed_code = ai_fix
                confidence = "Medium (AI Generated)"
            else:
                fixed_code = "No fix available"
                confidence = "Low"

        suggestions.append({
            "issue": issue,
            "file": path,
            "problem": message,
            "original": original_code,
            "fixed": fixed_code,
            "confidence": confidence
        })

    # =========================
    # PDF GENERATION
    # =========================
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        doc = SimpleDocTemplate(pdf_path)
        styles = getSampleStyleSheet()

        content = []

        content.append(Paragraph("Auto-Fix Code Report", styles["Title"]))
        content.append(Spacer(1, 10))

        content.append(Paragraph(f"Generated At: {datetime.now()}", styles["Normal"]))
        content.append(Spacer(1, 15))

        for s in suggestions:
            content.append(Paragraph(f"Issue: {s['issue']}", styles["Heading3"]))
            content.append(Paragraph(f"File: {s['file']}", styles["Normal"]))
            content.append(Paragraph(f"Problem: {s['problem']}", styles["Normal"]))
            content.append(Paragraph(f"Confidence: {s['confidence']}", styles["Normal"]))

            content.append(Spacer(1, 6))
            content.append(Paragraph("Vulnerable Code:", styles["Heading4"]))
            content.append(Paragraph(s["original"], styles["Normal"]))

            content.append(Spacer(1, 6))
            content.append(Paragraph("Fixed Code:", styles["Heading4"]))
            content.append(Paragraph(s["fixed"], styles["Normal"]))

            content.append(Spacer(1, 15))

        doc.build(content)

        print(f"\n🛠 Final Auto-fix PDF generated: {pdf_path}")

    except Exception as e:
        print(f"⚠ PDF generation failed: {e}")

    return pdf_path