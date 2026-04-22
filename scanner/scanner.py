import os
import sys
import subprocess
from ai_engine.explain import explain_issue

vulnerabilities_found = False
vulnerabilities = []

# ✅ Ignore internal folders
IGNORE_DIRS = {
    ".git",
    ".github",
    "__pycache__",
    "scanner",
    "ai_engine",
    "temp_repos"
}

# ✅ Ignore internal files
IGNORE_FILES = {
    "scanner.py",
    "rules.py",
    "explain.py",
    "test_hf_api.py",
    "test_dns.py"
}


def clone_repo(repo_url):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    os.makedirs("temp_repos", exist_ok=True)
    clone_path = f"temp_repos/{repo_name}_{os.getpid()}"

    print(f"🌐 Cloning repository into {clone_path}...\n")
    subprocess.run(["git", "clone", repo_url, clone_path], check=True)

    return clone_path


def run_scan(scan_path):
    global vulnerabilities_found, vulnerabilities

    print("🔍 Starting Security Scan...\n")

    for root, dirs, files in os.walk(scan_path):

        # ✅ remove ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:

            # ✅ ignore internal files only
            if file in IGNORE_FILES:
                continue

            # ✅ scan ALL python files (including test files)
            if not file.endswith(".py"):
                continue

            path = os.path.join(root, file)

            try:
                with open(path, "r", errors="ignore") as f:
                    code = f.read()

                    # 🔴 Rule 1: Hardcoded password
                    if "password" in code and "=" in code:
                        vulnerabilities.append({
                            "check_id": "HARDCODED_SECRET",
                            "path": path,
                            "start": {"line": 0},
                            "extra": {"message": "Hardcoded password detected"}
                        })
                        vulnerabilities_found = True

                    # 🔴 Rule 2: Unsafe eval
                    if "eval(" in code:
                        vulnerabilities.append({
                            "check_id": "UNSAFE_EVAL",
                            "path": path,
                            "start": {"line": 0},
                            "extra": {"message": "Use of eval() detected"}
                        })
                        vulnerabilities_found = True

                    # 🔴 Rule 3: Unsafe deserialization
                    if "pickle.load" in code:
                        vulnerabilities.append({
                            "check_id": "UNSAFE_DESERIALIZATION",
                            "path": path,
                            "start": {"line": 0},
                            "extra": {"message": "Unsafe deserialization using pickle"}
                        })
                        vulnerabilities_found = True

            except Exception as e:
                print(f"⚠ Could not read file {path}: {e}")


if __name__ == "__main__":

    # Case 1: Scan external repo
    if len(sys.argv) == 2:
        repo_url = sys.argv[1]
        repo_path = clone_repo(repo_url)

    # Case 2: Scan current repo (CI mode)
    else:
        print("🔄 Running in CI mode (Scanning current repository)\n")
        repo_path = "."

    run_scan(repo_path)

    # 🤖 AI Analysis
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

    # ✅ Final result
    if vulnerabilities_found:
        print("\n❌ Vulnerabilities Found! Failing the pipeline.")
        sys.exit(1)
    else:
        print("\n✅ No vulnerabilities found.")
        sys.exit(0)