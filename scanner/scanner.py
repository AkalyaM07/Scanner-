import os
import sys
import subprocess
import shutil

vulnerabilities_found = False


def clone_repo(repo_url):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    clone_path = f"temp_repos/{repo_name}"

    # Remove old cloned repo if exists
    if os.path.exists(clone_path):
        shutil.rmtree(clone_path)

    print(f"🌐 Cloning repository into {clone_path}...")
    subprocess.run(["git", "clone", repo_url, clone_path], check=True)

    return clone_path


def run_scan(scan_path):
    global vulnerabilities_found

    print("🔍 Starting Security Scan...\n")

    for root, dirs, files in os.walk(scan_path):

        # Optional: Skip .git directory
        if ".git" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)

                try:
                    with open(path, "r", errors="ignore") as f:
                        code = f.read()

                        # Rule 1: Hardcoded password (basic detection)
                        if "password" in code and "=" in code:
                            print(f"[!] HARDCODED_SECRET detected in {path}")
                            vulnerabilities_found = True

                        # Rule 2: Unsafe eval usage
                        if "eval(" in code:
                            print(f"[!] UNSAFE_EVAL detected in {path}")
                            vulnerabilities_found = True

                        # Rule 3: Unsafe deserialization
                        if "pickle.load" in code:
                            print(f"[!] UNSAFE_DESERIALIZATION detected in {path}")
                            vulnerabilities_found = True

                except Exception as e:
                    print(f"⚠ Could not read file {path}: {e}")


if __name__ == "__main__":

    # 🔹 Case 1: If GitHub URL provided → Clone & Scan
    if len(sys.argv) == 2:
        repo_url = sys.argv[1]
        repo_path = clone_repo(repo_url)

    # 🔹 Case 2 & 3: GitHub Actions (Push / Pull Request)
    else:
        print("🔄 Running in CI mode (Scanning current repository)")
        repo_path = "."

    run_scan(repo_path)

    if vulnerabilities_found:
        print("\n❌ Vulnerabilities Found! Failing the pipeline.")
        sys.exit(1)
    else:
        print("\n✅ No vulnerabilities found.")

    # Clean up cloned repo only in URL mode
    if len(sys.argv) == 2:
        shutil.rmtree(repo_path)