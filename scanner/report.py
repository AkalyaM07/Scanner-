import os
from datetime import datetime
from ai_engine.explain import explain_issue

def generate_report(vulnerabilities):

    os.makedirs("reports", exist_ok=True)

    pdf_path = "reports/report.pdf"

    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

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

        # Issues + AI
        for v in vulnerabilities:
            issue = v.get("check_id", "")
            path = v.get("path", "")
            message = v.get("extra", {}).get("message", "")

            # 🔥 THIS IS IMPORTANT
            try:
                ai_text = explain_issue(v)
            except:
                ai_text = "AI explanation not available"

            content.append(Paragraph(f"Issue: {issue}", styles["Normal"]))
            content.append(Paragraph(f"File: {path}", styles["Normal"]))
            content.append(Paragraph(f"Message: {message}", styles["Normal"]))
            content.append(Paragraph(f"AI Explanation: {ai_text}", styles["Normal"]))
            content.append(Spacer(1, 12))

        doc.build(content)

        print(f"\n📄 PDF Report generated: {pdf_path}")

    except Exception as e:
        print(f"⚠ PDF generation failed: {e}")

    return pdf_path