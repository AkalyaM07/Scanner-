import os
import requests
import time
from datetime import datetime

# =========================
# AI CONFIG (HuggingFace)
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
# RULE-BASED PATCH
# =========================
def rule_based_fix(issue, code):

    if issue == "HARDCODED_PASSWORD":
        return code.replace("password =", "password = os.getenv(")

    if issue == "DANGEROUS_EVAL":
        return code.replace("eval(", "ast.literal_eval(")

    if issue == "UNSAFE_DESERIALIZATION":
        return code.replace("pickle.load", "json.load")

    if issue == "COMMAND_INJECTION":
        return code.replace("os.system", "subprocess.run")

    return None


# =========================
# EXTRACT CODE SNIPPET
# =========================
def get_code_snippet(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read()[:500]   # first 500 chars only
    except:
        return "Could not read file"


# =========================
# MAIN FUNCTION
# =========================
def generate_autofix(vulnerabilities):

    os.makedirs("reports", exist_ok=True)
    pdf_path = "reports/autofix_report.pdf"

    suggestions = []

    for v in vulnerabilities:

        issue = v.get("check_id")
        path = v.get("path")
        message = v.get("extra", {}).get("message", "")

        original_code = get_code_snippet(path)

        # =========================
        # RULE FIX FIRST
        # =========================
        fixed_code = rule_based_fix(issue, original_code)

        # =========================
        # AI FIX IF RULE FAILS
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
            else:
                fixed_code = "No fix available"

        suggestions.append({
            "issue": issue,
            "file": path,
            "problem": message,
            "original": original_code,
            "fixed": fixed_code
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

            content.append(Spacer(1, 6))
            content.append(Paragraph("Vulnerable Code:", styles["Heading4"]))
            content.append(Paragraph(s["original"], styles["Normal"]))

            content.append(Spacer(1, 6))
            content.append(Paragraph("Fixed Code:", styles["Heading4"]))
            content.append(Paragraph(s["fixed"], styles["Normal"]))

            content.append(Spacer(1, 15))

        doc.build(content)

        print(f"\n🛠 Advanced Auto-fix PDF generated: {pdf_path}")

    except Exception as e:
        print(f"⚠ PDF generation failed: {e}")

    return pdf_path