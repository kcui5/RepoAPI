import os

import github_utils
import pkg_utils
import create_apis

"""ADD PRINT STATEMENTS TO MONITOR WHAT YOURE DOING FOR LARGER GITHUB REPOS!!!!








UNKNOWN BEHAVIOR FOR NESTED FUNCTIONS OR FUNCTIONS IN CLASSES ETC.....



APIs CREATED DO NOT INPUT ARGUMENTS THAT PREVIOUSLY WERE INPUTTED IN ORIGINAL FUNCTION THAT ALSO TAKES ARGPARSE ARGS




**************"""

test_repo = "git@github.com:kcui5/pd_modal.git"
apis = ["pd_home.getSum", "pd_alt.getSumTwo"]
args = {
    apis[0]: ["x: int", "y: int = 10"]
}
args = create_apis.fill_empty_api_args(apis, args)

gpu_type = "A100"
gpu_type = ""

def from_local_package():

    conda_env_name = "testcondaenv"
    
    if not github_utils.is_valid_github_url(test_repo):
        print("Link invalid!")
        exit()
    else:
        print(f"Cloning repo from {test_repo}...")
    print(github_utils.clone_repo(test_repo))
    
    repo_name = github_utils.get_repo_name(test_repo)
    print(f"Repository Name: {repo_name}")

    repo_path = os.path.join(os.getcwd(), "package", "src", repo_name)
    
    pkg_utils.recursively_fix_imports(repo_path)
    print("Fixed imports")
    
    pkg_utils.fix_all_argparse(repo_path, apis, args)
    print("Fixed argparse arguments")
    
    pkg_utils.create_init_file(repo_path, apis)
    print("Created init file")
    
    pkg_utils.create_setup_file(repo_path, repo_name)
    print("Created setup file")

    pkg_utils.create_manifest_file()
    print("Created manifest file")
    
    create_apis.create_api_file_from_local_pkg(apis, args, repo_name, gpu_type)
    print("Created API file")

    pkg_utils.conda_pip_install(conda_env_name)
    print(f"Installed local package into conda env {conda_env_name}")
    
    print("Serving APIs on modal...")
    create_apis.serve_apis(conda_env_name, apis)

from_local_package()

"""docker_link = "liuyuanpal/syncdreamer-env:latest"
apis = ["generate.main"]
args = {
    apis[0]: ["ckpt", "input", "output", "sample_num", "cfg_scale", "elevation", "crop_size"]
}
args = create_apis.fill_empty_api_args(apis, args)
    
def from_docker_image():
    create_apis.create_api_file_from_docker(docker_link, apis, args, gpu_type)
    print("Created API file")

#from_docker_image()"""