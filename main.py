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

repo_name = githubutils.get_repo_name(test_repo)
print(repo_name)
"""

repo_name = "pd_modal"

#pkgutils.recursively_fix_imports(repo_name)

