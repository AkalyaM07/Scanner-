import os
import sys
import subprocess
from ai_engine.explain import explain_issue
from scanner.report import generate_report
from scanner.autofix import generate_autofix
from scanner.rules import check_code   # ✅ NEW

vulnerabilities_found = False
vulnerabilities = []

# ✅ Ignore internal folders
IGNORE_DIRS = {
    ".git",
    ".github",
    "__pycache__",
    "scanner",
    "ai_engine",
    "temp_repos",
    "reports"
}

# ✅ Ignore internal files
IGNORE_FILES = {
    "scanner.py",
    "rules.py",
    "explain.py",
    "report.py",
    "autofix.py"
}


# =========================
# CLONE REPO
# =========================
def clone_repo(repo_url):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    os.makedirs("temp_repos", exist_ok=True)
    clone_path = f"temp_repos/{repo_name}_{os.getpid()}"

    print(f"🌐 Cloning repository into {clone_path}...\n")
    subprocess.run(["git", "clone", repo_url, clone_path], check=True)

    return clone_path


# =========================
# SCANNER USING RULES.PY
# =========================
def run_scan(scan_path):
    global vulnerabilities_found, vulnerabilities

    print("🔍 Starting Security Scan...\n")

    for root, dirs, files in os.walk(scan_path):

        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:

            if file in IGNORE_FILES:
                continue

            if not file.endswith(".py"):
                continue

            path = os.path.join(root, file)

            try:
                with open(path, "r", errors="ignore") as f:
                    code = f.read()

                    # ✅ USE RULE ENGINE
                    issues = check_code(code)

                    for issue in issues:
                        vulnerabilities.append({
                            "check_id": issue,
                            "path": path,
                            "start": {"line": 0},
                            "extra": {
                                "message": issue.replace("_", " ").title()
                            }
                        })
                        vulnerabilities_found = True

            except Exception as e:
                print(f"⚠ Could not read file {path}: {e}")


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    if len(sys.argv) == 2:
        repo_url = sys.argv[1]
        repo_path = clone_repo(repo_url)
    else:
        print("🔄 Running in CI mode (Scanning current repository)\n")
        repo_path = "."

    run_scan(repo_path)

    # =========================
    # 🤖 AI ANALYSIS
    # =========================
    if vulnerabilities:
        print("\n🤖 AI Analysis Started...\n")

        for issue in vulnerabilities:
            try:
                result = explain_issue(issue)
                print("\n==============================")
                print(result)
                print("==============================\n")
            except Exception as e:
                print(f"⚠ AI analysis failed: {e}")

    # =========================
    # 📄 REPORT
    # =========================
    generate_report(vulnerabilities)

    # =========================
    # 🛠 AUTO-FIX
    # =========================
    generate_autofix(vulnerabilities)

    # =========================
    # FINAL STATUS
    # =========================
    if vulnerabilities_found:
        print("\n❌ Vulnerabilities Found! Failing the pipeline.")
        sys.exit(1)
    else:
        print("\n✅ No vulnerabilities found.")
        sys.exit(0)