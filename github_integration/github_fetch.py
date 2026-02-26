from git import Repo
import os
import shutil

def clone_repo(repo_url):
    folder_name = repo_url.split("/")[-1].replace(".git", "")
    clone_path = os.path.join("temp_repos", folder_name)

    os.makedirs("temp_repos", exist_ok=True)

    if os.path.exists(clone_path):
        shutil.rmtree(clone_path)

    Repo.clone_from(repo_url, clone_path)

    return clone_path