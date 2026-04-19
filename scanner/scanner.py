import os
import sys
import subprocess
from ai_engine.explain import explain_issue   # ✅ fixed import

vulnerabilities_found = False
vulnerabilities = []


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

        if ".git" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)

                try:
                    with open(path, "r", errors="ignore") as f:
                        code = f.read()

                        # Rule 1: Hardcoded password
                        if "password" in code and "=" in code:
                            vuln = {
                                "check_id": "HARDCODED_SECRET",
                                "path": path,
                                "start": {"line": 0},
                                "extra": {"message": "Hardcoded password detected"}
                            }
                            vulnerabilities.append(vuln)
                            vulnerabilities_found = True

                        # Rule 2: Unsafe eval
                        if "eval(" in code:
                            vuln = {
                                "check_id": "UNSAFE_EVAL",
                                "path": path,
                                "start": {"line": 0},
                                "extra": {"message": "Use of eval() detected"}
                            }
                            vulnerabilities.append(vuln)
                            vulnerabilities_found = True

                        # Rule 3: Unsafe deserialization
                        if "pickle.load" in code:
                            vuln = {
                                "check_id": "UNSAFE_DESERIALIZATION",
                                "path": path,
                                "start": {"line": 0},
                                "extra": {"message": "Unsafe deserialization using pickle"}
                            }
                            vulnerabilities.append(vuln)
                            vulnerabilities_found = True

                except Exception as e:
                    print(f"⚠ Could not read file {path}: {e}")


if __name__ == "__main__":

    # Case 1: URL mode
    if len(sys.argv) == 2:
        repo_url = sys.argv[1]
        repo_path = clone_repo(repo_url)

    # Case 2: Local / GitHub Actions
    else:
        print("🔄 Running in CI mode (Scanning current repository)\n")
        repo_path = "."

    run_scan(repo_path)

    # 🤖 AI Analysis
    if vulnerabilities:
        print("\n🤖 AI Analysis Started...\n")

        for issue in vulnerabilities:
            try:
                result = explain_issue(issue)   # ✅ correct function
                print("\n==============================")
                print(result)
                print("==============================\n")
            except Exception as e:
                print(f"⚠ AI analysis failed: {e}")

    # Final status
    if vulnerabilities_found:
        print("\n❌ Vulnerabilities Found! Failing the pipeline.")
        sys.exit(1)
    else:
        print("\n✅ No vulnerabilities found.")
        sys.exit(0)