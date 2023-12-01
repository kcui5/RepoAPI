import subprocess
import re
import os

def validate_https_github_url(url):
    # Regular expression for a basic GitHub repo https URL pattern
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
        return validate_https_github_url(url)
    else:
        return validate_ssh_github_url(url)
    
def is_valid_docker_link(link):
    """
    Validates whether the provided link is a valid Docker Env link.
    
    Args:
    link (str): The link to validate.
    
    Returns:
    bool: True if valid, False otherwise.
    """
    regex = r"[a-zA-Z0-9][a-zA-Z0-9\.-]*\/[a-zA-Z0-9_\/-]+(:[a-zA-Z0-9\._-]+)?"

    if len(link) > 200:
        return False
    
    return bool(re.match(regex, link))

def clone_repo(repo_url, repo_path):
    """
    Clones a GitHub repository into the given repo_path path.

    Args:
    repo_url (str): The URL of the GitHub repository.
    repo_path (os.path): The target directory location to clone the GitHub repository into.

    Returns:
    str: Output message of the clone operation.
    """
    try:
        os.makedirs(repo_path)
        subprocess.check_call(['git', 'clone', repo_url, repo_path])
        return f"Successfully cloned {repo_url}"
    except subprocess.CalledProcessError as e:
        return f"An error occurred while cloning {repo_url}: {e}"

def get_repo_name(repo_url):
    """
    Extracts the name of the GitHub repository.
    
    Args:
    repo_url (str): The URL of the GitHub repository.
    
    Returns:
    str: Name of the GitHub repository
    """
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