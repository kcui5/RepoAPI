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

"""
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
def from_local_package(local_repo, local_apis, local_args, local_gpu_type):
    repo_name = github_utils.get_repo_name(local_repo)
    print(f"Repository Name: {repo_name}")
    repo_path = os.path.join(os.getcwd(), "package", "src", repo_name)
    conda_env_name = f"{repo_name}"
    
    if not github_utils.is_valid_github_url(local_repo):
        print("Link invalid!")
        return
    else:
        print(f"Cloning repo from {local_repo}...")
    print(github_utils.clone_repo(local_repo))
    
    pkg_utils.recursively_fix_imports(repo_path, repo_name)
    print("Fixed imports")
    
    local_args = create_apis.fill_empty_api_args(local_apis, local_args)
    pkg_utils.fix_all_argparse(repo_path, local_apis, local_args)
    print("Fixed argparse arguments")
    
    pkg_utils.create_init_file(repo_path, local_apis)
    print("Created init file")
    
    pkg_utils.create_setup_file(repo_path, repo_name)
    print("Created setup file")

    pkg_utils.create_manifest_file()
    print("Created manifest file")
    
    create_apis.create_api_file_from_local_pkg(local_apis, local_args, repo_name, repo_path, local_gpu_type)
    print("Created API file")

    pkg_utils.conda_install_packages(conda_env_name)
    print("Installed package with conda")

    #pkg_utils.pip_install_packages()
    #print("Installed package with pip")

    print("Serving APIs...")
    #create_apis.serve_apis(local_apis)
    create_apis.serve_apis_conda(conda_env_name, local_apis)

#from_local_package(local_repo, local_apis, local_args, local_gpu_type)
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
def from_docker_image(docker_repo, docker_link, docker_apis, docker_args, docker_gpu_type):
    repo_name = github_utils.get_repo_name(docker_repo)
    print(f"Repository Name: {repo_name}")
    repo_path = os.path.join(os.getcwd(), "package", "src", repo_name)
    conda_env_name = f"{repo_name}"
    
    if not github_utils.is_valid_github_url(docker_repo):
        print("Link invalid!")
        exit()
    else:
        print(f"Cloning repo from {docker_repo}...")
    print(github_utils.clone_repo(docker_repo))
    
    pkg_utils.recursively_fix_imports(repo_path, repo_name)
    print("Fixed imports")
    
    docker_args = create_apis.fill_empty_api_args(docker_apis, docker_args)
    pkg_utils.fix_all_argparse(repo_path, docker_apis, docker_args)
    print("Fixed argparse arguments")
    
    pkg_utils.create_init_file(repo_path, docker_apis)
    print("Created init file")
    
    pkg_utils.create_setup_file(repo_path, repo_name)
    print("Created setup file")

    pkg_utils.create_manifest_file()
    print("Created manifest file")
    
    create_apis.create_api_file_from_docker(docker_apis, docker_args, docker_link, repo_name, repo_path, docker_gpu_type)
    print("Created API file")
    
    pkg_utils.conda_pip_install(conda_env_name)
    print(f"Installed local package into conda env {conda_env_name}")
    
    print("Serving APIs on modal...")
    create_apis.serve_apis(conda_env_name, docker_apis)

#from_docker_image()
