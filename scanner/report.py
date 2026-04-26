import json
import os
from datetime import datetime
from ai_engine.explain import explain_issue   # ✅ ADD THIS


def generate_report(vulnerabilities):
    os.makedirs("reports", exist_ok=True)

    json_path = "reports/report.json"

    with open(json_path, "w") as f:
        json.dump(
            {
                "total_vulnerabilities": len(vulnerabilities),
                "issues": vulnerabilities
            },
            f,
            indent=4
        )

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    pdf_path = "reports/report.pdf"

    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()

    content = []

    # Title
    content.append(Paragraph("Security Scan Report", styles["Title"]))
    content.append(Spacer(1, 10))

    # Summary
    content.append(Paragraph(f"Total Vulnerabilities: {len(vulnerabilities)}", styles["Normal"]))
    content.append(Paragraph(f"Generated At: {datetime.now()}", styles["Normal"]))
    content.append(Spacer(1, 15))

    # =========================
    # 🔥 ADD AI EXPLANATION HERE
    # =========================

    for v in vulnerabilities:

        issue = v.get("check_id", "")
        path = v.get("path", "")
        message = v.get("extra", {}).get("message", "")

        # Basic info
        content.append(Paragraph(f"Issue: {issue}", styles["Normal"]))
        content.append(Paragraph(f"File: {path}", styles["Normal"]))
        content.append(Paragraph(f"Message: {message}", styles["Normal"]))

        # 🤖 AI Explanation
        try:
            ai_text = explain_issue(v)
        except:
            ai_text = "AI explanation not available"

        content.append(Paragraph("AI Explanation:", styles["Heading3"]))
        content.append(Paragraph(ai_text.replace("\n", "<br/>"), styles["Normal"]))

        content.append(Spacer(1, 15))

    doc.build(content)

    print(f"\nPDF Report generated: {pdf_path}")

    return pdf_path