import os
from scanner.rules import check_file


def scan_path(repo_path):
    """
    Scan all files in the given repository path
    """
    results = []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                issues = check_file(file_path)
                for issue in issues:
                    results.append((issue, file_path))
            except Exception:
                # skip unreadable files
                pass

    return results


# ✅ This allows manual running also
if __name__ == "__main__":
    print("🔍 Scanning repository...")

    findings = scan_path(".")

    if not findings:
        print("✅ No vulnerabilities found")
    else:
        print("\n⚠️ Vulnerabilities detected:\n")
        for issue, path in findings:
            print(f"{issue} → {path}")