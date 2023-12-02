import os

import github_utils
import pkg_utils
import create_apis

"""
UNKNOWN BEHAVIOR FOR NESTED FUNCTIONS OR FUNCTIONS IN CLASSES ETC.....

APIs CREATED DO NOT INPUT ARGUMENTS THAT PREVIOUSLY WERE INPUTTED IN ORIGINAL FUNCTION THAT ALSO TAKES ARGPARSE ARGS

DOES NOT SUPPORT REQUIREMENTS IN REQUIREMENTS.TXT THAT DON'T MATCH THEIR PACKAGE NAME

DOES NOT WORK IF ANY LOCAL PACKAGE FOLDER OR FILE OR FUNCTION HAS 'TORCH'


MOUNT VOLUMES ???

APIS IN PYTHON FILES IN FOLDERS???

"""
GPU_TYPES = {"A100", "A10G", "L4", "T4", "INF2", "ANY"}

def validate_inputs(repo_link, docker_link, apis, gpu_type):
    """Returns an error message if there is an invalid input, otherwise returns None."""
    if not apis:
        error_msg = "No APIs given!"
        print(error_msg)
        return error_msg
    if gpu_type and gpu_type not in GPU_TYPES:
        error_msg = "Invalid GPU!"
        print(error_msg)
        return error_msg
    if not github_utils.is_valid_github_url(repo_link):
        error_msg = "Invalid GitHub link!"
        print(error_msg)
        return error_msg
    if docker_link and not github_utils.is_valid_docker_link(docker_link):
        error_msg = "Invalid Docker link!"
        print(error_msg)
        return error_msg
    
    return None

def run(repo_link, docker_link, apis, gpu_type):
    valid_inputs_result = validate_inputs(repo_link, docker_link, apis, gpu_type)
    if valid_inputs_result:
        return valid_inputs_result
    
    repo_name = github_utils.get_repo_name(repo_link)
    if not repo_name:
        error_msg = "Error processing GitHub repository!"
        print(error_msg)
        return error_msg
    print(f"Repository Name: {repo_name}")
    repo_path = os.path.join(os.getcwd(), repo_name, "src", repo_name)
    api_file_path = os.path.join(os.getcwd(), f"{repo_name}_apis.py")
    conda_env_name = f"{repo_name}"
    
    if not os.path.exists(repo_path):
        print(f"Cloning repo from {repo_link}...")
        clone_result = github_utils.clone_repo(repo_link, repo_path)
        print(clone_result)
        if clone_result.startswith("An error occurred"):
            return clone_result
        
        fix_imports_result = pkg_utils.recursively_fix_imports(repo_path, repo_name)
        print(fix_imports_result)
        if fix_imports_result == "No requirements.txt file!":
            return fix_imports_result
        
        print("Skipping argparse fixing...")
        
        pkg_utils.create_init_file(repo_path, apis)
        print("Created init file")
        
        pkg_utils.create_setup_file(repo_name)
        print("Created setup file")

        pkg_utils.create_manifest_file(repo_name)
        print("Created manifest file")
        
        if docker_link:
            create_apis.create_api_file_from_docker(api_file_path, apis, docker_link, repo_name, repo_path, gpu_type)
            print("Created API file from docker")
        else:
            create_apis.create_api_file_from_local_pkg(api_file_path, apis, repo_name, repo_path, gpu_type)
            print("Created API file from local package")

    conda_install_result = pkg_utils.conda_install_packages(conda_env_name, repo_name)
    print(conda_install_result)
    if conda_install_result.startswith("Error"):
        return conda_install_result

    print("Serving APIs...")
    create_apis.serve_apis_conda(conda_env_name, api_file_path, repo_name, apis)

#Example calls:
"""
local_repo = "git@github.com:kcui5/pd_modal.git"
local_apis = ["pd_home.getSum"]
local_args = {
    local_apis[0]: [
        "x: int",
        "y: int = 40"
    ]
}
local_args = create_apis.fill_empty_api_args(local_apis, local_args)
local_gpu_type = ""
"""

"""
docker_repo = "git@github.com:liuyuan-pal/SyncDreamer.git"
docker_link = "liuyuanpal/syncdreamer-env:latest"
docker_apis = ["generate.main", "train_syncdreamer.get_node_name"]
docker_args = {
    docker_apis[0]: [
        "output: str", 
        "input: str",
        "elevation: float",
        "cfg: str = 'configs/syncdreamer.yaml'",
        "ckpt: str = 'ckpt/syncdreamer-step80k.ckpt'",
        "sample_num: int = 4",
        "crop_size: int = -1",
        "cfg_scale: float = 2.0",
        "batch_view_num: int = 8",
        "seed: int = 6033",
        "sampler: str = 'ddim'",
        "sample_steps: int = 50",
    ],
    docker_apis[1]: [
        "name",
        "parent_name",
    ]
}
docker_args = create_apis.fill_empty_api_args(docker_apis, docker_args)
docker_gpu_type = "A100"
"""