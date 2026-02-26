import os
from scanner.rules import check_vulnerabilities


def scan_repository(repo_path):
    findings = []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            # ✅ MULTI-LANGUAGE SUPPORT
            if file.endswith((".py", ".js", ".ts")):
                full_path = os.path.join(root, file)

                try:
                    with open(full_path, "r", errors="ignore") as f:
                        code = f.read()

                    issues = check_vulnerabilities(code)

                    for issue in issues:
                        findings.append({
                            "file": full_path,
                            "issue": issue
                        })

                except Exception:
                    pass

    return findings


# 🔥 REAL GITHUB TEST
if __name__ == "__main__":
    from github_integration.github_fetch import clone_repo

    print("🔄 Cloning real GitHub repo...")
    repo_path = clone_repo(
        "https://github.com/juice-shop/juice-shop"
    )

    print("🔍 Scanning repository...\n")

    results = scan_repository(repo_path)

    if not results:
        print("✅ No vulnerabilities found")
    else:
        print("⚠️ Vulnerabilities detected:\n")
        for r in results:
            print(f"{r['issue']} → {r['file']}")