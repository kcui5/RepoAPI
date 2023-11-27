import modal
from typing import Dict

import main

stub = modal.Stub()
git_image = modal.Image.debian_slim().apt_install('git')

@stub.function(image=git_image)
@modal.web_endpoint()
def entry(inputs: Dict):
    repo_link: str = inputs['repo_link']
    docker_link: str = inputs['docker_link'] if 'docker_link' in inputs else ""
    apis: list = inputs['apis']
    args: dict = inputs['args'] if 'args' in inputs else {}
    gpu_type: str = inputs['gpu_type'] if 'gpu_type' in inputs else ""
    print(repo_link)

    if not docker_link:
        main.from_local_package(repo_link, apis, args, gpu_type)
    else:
        main.from_docker_image(repo_link, docker_link, apis, args, gpu_type)
    import subprocess
    subprocess.run("ls -a", shell=True)

@stub.function(image=git_image)
@modal.web_endpoint()
def all_apis(inputs: Dict):
    import subprocess
    subprocess.run("ls -a", shell=True)
    import repo_apis
    func_name : str = inputs['func_name']
    func = getattr(repo_apis, func_name)
    if callable(func):
        return func(inputs)
    else:
        print("not callable")
