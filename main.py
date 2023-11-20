import os

import githubutils
import pkgutils

test_repo = "git@github.com:kcui5/pd_modal.git"
"""
if not githubutils.is_valid_github_url(test_repo):
    print("Link invalid!")
    exit()
else:
    print("Cloning repo...")
print(githubutils.clone_repo(test_repo))
"""
repo_name = githubutils.get_repo_name(test_repo)
print(f"Repository Name: {repo_name}")

repo_path = os.path.join(os.getcwd(), "package", "src", repo_name)
"""
pkgutils.recursively_fix_imports(repo_path)
print("Fixed imports")
pkgutils.create_init_file(repo_path)
print("Created init file")
"""
pkgutils.create_setup_file(repo_path, repo_name)
print("Created setup file")
