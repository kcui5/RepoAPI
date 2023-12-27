import subprocess
import os

import pkg_utils

def get_api_func_signature(func_name, func_call, repo, img=None, gpu=None):
    decorator_args = []
    if img:
        decorator_args.append(f'image={img}')
    if repo:
        decorator_args.append(f'mounts=[modal.Mount.from_local_python_packages("{repo}")]')
    if gpu:
        decorator_args.append(f'gpu="{gpu}"')
    decorator_args_str = ", ".join(decorator_args)
    stub_function_decorator = f'@stub.function({decorator_args_str})'


    func_call_str = f"""import {repo}

    res = {repo}.{func_call}(**inputs)"""

    res_string = """res_json = {
        "status": "200",
        "data": {
            "res": f'{res}'
        }
    }
"""

    content = f"""{stub_function_decorator}
@modal.web_endpoint()
def {func_name}(inputs: Dict):
    {func_call_str}
    {res_string}
    print(res_json)
    res_json = json.dumps(res_json)
    return res_json

"""
    return content

def create_api_file_from_local_pkg(api_file_path, api_function_calls, repo_name, repo_path, gpu_type):
    api_function_names = ["_".join(func.split('.')) for func in api_function_calls]

    content = f"""import json
from typing import Dict
import modal

stub = modal.Stub()

img = modal.Image.debian_slim()
dependencies = {list(pkg_utils.get_external_packages(repo_path))}
for d in dependencies:
    img = img.pip_install(d)

"""
    for i in range(len(api_function_calls)):
        content += get_api_func_signature(api_function_names[i], api_function_calls[i], repo_name, img="img", gpu=gpu_type)
    
    with open(api_file_path, 'w') as file:
        file.write(content)

def create_api_file_from_docker(api_file_path, api_function_calls, docker_link, repo_name, gpu_type):
    api_function_names = ["_".join(func.split('.')) for func in api_function_calls]

    content = f"""import json
from typing import Dict
import modal

stub = modal.Stub()
docker_img = modal.Image.from_registry("{docker_link}")

"""
    for i in range(len(api_function_calls)):
        content += get_api_func_signature(api_function_names[i], api_function_calls[i], repo_name, img="docker_img", gpu=gpu_type)

    with open(api_file_path, 'w') as file:
        file.write(content)

def get_api_links(repo_name, apis):
    apis = ["-".join(s.split('.')) for s in apis]
    apis = ["-".join(s.split("_")) for s in apis]
    apis = [s.lower() for s in apis]
    repo_name = "-".join(repo_name.split('.'))
    repo_name = "-".join(repo_name.split('_'))
    repo_name = f"{repo_name}-apis-py"
    api_links = [f"https://kcui5--{repo_name}-{s}-dev.modal.run" for s in apis]
    return api_links

def serve_apis(apis, api_file_path):
    try:        
        serve_command = f"modal serve {api_file_path}"
        print(get_api_links(apis))
        #activate_command = "source /pkgsvenv/bin/activate"
        activate_command = 'export PATH="/pkg:$PATH"'
        subprocess.run(f"{activate_command} && {serve_command}", shell=True, check=True, executable="/bin/bash")
    except subprocess.CalledProcessError as e:
        print("Error serving APIs: ", e)
        exit()

def serve_apis_conda(conda_env_name, api_file_path, repo_name, apis):
    serve_command = f"conda run --name {conda_env_name} modal serve {api_file_path}"
    print(serve_command)
    print(get_api_links(repo_name, apis))
    #subprocess.run(serve_command, shell=True, check=True, timeout=60)
    serving_process = subprocess.Popen(serve_command, shell=True)
    try:
        serving_process.wait(timeout=60)
    except subprocess.TimeoutExpired:
        serving_process.terminate()
        print("Done serving.")
        return
    
def serve_apis_venv(venv_name, api_file_path):
    modal_executable = os.path.join(venv_name, 'bin', 'modal')
    serve_command = f"{modal_executable} serve {api_file_path}"
    try:
        serving_process = subprocess.Popen(serve_command, shell=True)
        print("serving")
        serving_process.wait(timeout=60)
    except subprocess.TimeoutExpired:
        serving_process.terminate()
        print("Done serving.")
        return
