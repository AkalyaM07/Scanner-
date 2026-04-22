import json
import os

def generate_report(vulnerabilities):
    report_data = {
        "total_vulnerabilities": len(vulnerabilities),
        "issues": vulnerabilities
    }

    # create reports folder
    os.makedirs("reports", exist_ok=True)

    file_path = "reports/report.json"

    with open(file_path, "w") as f:
        json.dump(report_data, f, indent=4)

    print(f"\n📄 Report generated: {file_path}")

    return file_path