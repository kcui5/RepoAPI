import subprocess
import re
from urllib.parse import urlparse

def is_valid_github_url(url):
    """
    Validates whether the provided URL is a valid GitHub repository URL.

    Args:
    url (str): The URL to validate.

    Returns:
    bool: True if valid, False otherwise.
    """
    # Regular expression for a basic GitHub repo URL pattern
    regex = r'^https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/?$'

    if len(url) > 200:
        return False
    
    if not re.match(regex, url):
        return False

    # Parse the URL
    parsed_url = urlparse(url)

    # Check the scheme
    if parsed_url.scheme != 'https':
        return False

    # Check the network location
    if parsed_url.netloc != 'github.com':
        return False

    # Check the path (expecting two parts: /username/repository)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) != 2 or not all(path_parts):
        return False

    # Ensure no query string or fragment
    if parsed_url.query or parsed_url.fragment:
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
