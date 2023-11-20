import subprocess
import re

def is_valid_github_url(url):
    """
    Validates whether the provided URL is a valid GitHub repository URL.

    Args:
    url (str): The URL to validate.

    Returns:
    bool: True if valid, False otherwise.
    """
    # Regular expression for a basic GitHub repo URL pattern
    regex = r'^git@github\.com:[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+\.git$'

    if len(url) > 200:
        return False
    
    if not re.match(regex, url):
        return False
    
    parts = url.split(':')
    if len(parts) != 2 or parts[0] != "git@github.com":
        return False
    username, repository = parts[1].split('/')
    if not username or not repository:
        return False

    return True

def clone_repo(repo_url, target_dir=None):
    """
    Clones a GitHub repository.

    Args:
    repo_url (str): The URL of the GitHub repository.
    target_dir (str, optional): Directory where to clone the repo. If None, installs in the cwd.

    Returns:
    str: Output message of the clone operation.
    """
    try:
        if target_dir:
            subprocess.check_call(['git', 'clone', repo_url, target_dir])
        else:
            subprocess.check_call(['git', 'clone', repo_url])
        return f"Successfully cloned {repo_url}"
    except subprocess.CalledProcessError as e:
        return f"An error occurred while cloning {repo_url}: {e}"

def get_repo_name(repo_url):
    parts = repo_url.split('/')
    if len(parts) != 2:
        print("Unrecognized github repository ssh url!")
        return
    repo_name = parts[1]
    if not repo_name.endswith('.git'):
        print("Unrecognized github repository ssh url!")
        return
    return repo_name[:-4]