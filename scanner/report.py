import json
import os
from datetime import datetime

def generate_report(vulnerabilities):

    # 📁 Create reports folder
    os.makedirs("reports", exist_ok=True)

    # =========================
    # ✅ JSON (backup)
    # =========================
    json_path = "reports/report.json"
    with open(json_path, "w") as f:
        json.dump({
            "total_vulnerabilities": len(vulnerabilities),
            "issues": vulnerabilities
        }, f, indent=4)

    # =========================
    # ✅ PDF REPORT (NO TRY-EXCEPT)
    # =========================
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

    # Issues
    for v in vulnerabilities:
        content.append(Paragraph(f"Issue: {v['check_id']}", styles["Normal"]))
        content.append(Paragraph(f"File: {v['path']}", styles["Normal"]))
        content.append(Paragraph(f"Message: {v['extra']['message']}", styles["Normal"]))
        content.append(Spacer(1, 10))

    doc.build(content)

    print(f"\n📕 PDF Report generated: {pdf_path}")

    return pdf_path