from githubutils import *
from pkgutils import *

test_repo = ""
if not is_valid_github_url(test_repo):
    print("Link invalid!")
clone_repo(test_repo)

