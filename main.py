import os

import github_utils
import pkg_utils
import create_apis

test_repo = "git@github.com:kcui5/pd_modal.git"
apis = ["pd_home.getSum"]
gpu_type = "A100"

def from_local_package():

    conda_env_name = "testcondaenv"
    
    if not github_utils.is_valid_github_url(test_repo):
        print("Link invalid!")
        exit()
    else:
        print("Cloning repo...")
    print(github_utils.clone_repo(test_repo))
    
    repo_name = github_utils.get_repo_name(test_repo)
    print(f"Repository Name: {repo_name}")

    repo_path = os.path.join(os.getcwd(), "package", "src", repo_name)
    
    pkg_utils.recursively_fix_imports(repo_path)
    print("Fixed imports")

    pkg_utils.create_init_file(repo_path, apis)
    print("Created init file")
    
    pkg_utils.create_setup_file(repo_path, repo_name)
    print("Created setup file")

    pkg_utils.create_manifest_file()
    print("Created manifest file")

    create_apis.create_api_file_from_local_pkg(apis, repo_name, gpu_type)
    print("Created API file")

    pkg_utils.conda_pip_install(conda_env_name)
    print(f"Installed local package into conda env {conda_env_name}")
    
    print("Serving APIs on modal...")
    create_apis.serve_apis(conda_env_name, apis)

docker_link = "liuyuanpal/syncdreamer-env:latest"
apis = ["generate.main"]
args = {
    apis[0]: ["ckpt", "input", "output", "sample_num", "cfg_scale", "elevation", "crop_size"]
}
    
def from_docker_image():
    create_apis.create_api_file_from_docker(docker_link, apis, args, gpu_type)
    print("Created API file")

from_docker_image()