import subprocess
import re
import os

def validate_https_github_url(url):
    regex = r'^https://github\.com/[\w.-]+/[\w.-]+(?:\.git)?$'

    if len(url) > 200:
        return False
    
    if not re.match(regex, url):
        return False

    return True

def validate_ssh_github_url(url):
    # Regular expression for a basic GitHub repo ssh URL pattern
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

def is_valid_github_url(url):
    """
    Validates whether the provided URL is a valid GitHub repository URL.

    Args:
    url (str): The URL to validate.

    Returns:
    bool: True if valid, False otherwise.
    """
    if url.startswith('https://'):
        print("https")
        return validate_https_github_url(url)
    else:
        return validate_ssh_github_url(url)

def clone_repo(repo_url):
    """
    Clones a GitHub repository into /package/src/.

    Args:
    repo_url (str): The URL of the GitHub repository.

    Returns:
    str: Output message of the clone operation.
    """
    try:
        target_dir=os.path.join(os.getcwd(), "package", "src", get_repo_name(repo_url))
        os.makedirs(target_dir)
        subprocess.check_call(['git', 'clone', repo_url, target_dir])
        return f"Successfully cloned {repo_url}"
    except subprocess.CalledProcessError as e:
        return f"An error occurred while cloning {repo_url}: {e}"

def get_repo_name(repo_url):
    if repo_url.startswith('https://'):
        parts = repo_url.split('/')
        if len(parts) != 5:
            print("Unrecognized github repository https url!")
            return
        repo_name = parts[-1]
        if not repo_name.endswith('.git'):
            print("Unrecognized github repository https url!")
        return repo_name[:-4]
    else:
        parts = repo_url.split('/')
        if len(parts) != 2:
            print("Unrecognized github repository ssh url!")
            return
        repo_name = parts[1]
        if not repo_name.endswith('.git'):
            print("Unrecognized github repository ssh url!")
            return
        return repo_name[:-4]