import os
import subprocess
import json

def get_api_func_signature(func_name, func_call, func_args, img=None, repo=None, gpu=None):
    res_string = """res_json = {
        "status": "200",
        "data": {
            "res": f'{res}'
        }
    }
"""
    decorator_args = []
    if img:
        decorator_args.append(f'image={img}')
    if repo:
        decorator_args.append(f'mounts=[modal.Mount.from_local_python_packages("{repo}")]')
    if gpu:
        decorator_args.append(f'gpu="{gpu}"')
    decorator_args_str = ", ".join(decorator_args)
    stub_function_decorator = f'@stub.function({decorator_args_str})'

    func_args_str = ", ".join([f"{arg.split(':')[0]}" for arg in func_args])
    if repo:
        func_call_str = f'res = {repo}.{func_call}({func_args_str})'
    else:
        func_call_str = f'res = {func_call}({func_args_str})'

    content = f"""{stub_function_decorator}
@modal.web_endpoint()
def {func_name}({", ".join(func_args)}):
    {func_call_str}
    {res_string}
    print(res_json)
    res_json = json.dumps(res_json)
    return res_json
    
"""
    return content

def fill_empty_api_args(apis, args):
    for api in apis:
        if api in args:
            continue
        else:
            args[api] = []
    return args

def create_api_file_from_local_pkg(api_function_calls, apis_args, repo_name, gpu_type):
    api_file_path = os.path.join(os.getcwd(), "modal_apis.py")

    api_function_names = ["_".join(func.split('.')) for func in api_function_calls]

    content = f"""import json
import modal
import {repo_name}

stub = modal.Stub()

"""
    for i in range(len(api_function_calls)):
        api_args = apis_args[api_function_calls[i]]
        content += get_api_func_signature(api_function_names[i], api_function_calls[i], api_args, repo=repo_name, gpu=gpu_type)
    
    with open(api_file_path, 'w') as file:
        file.write(content)

def create_api_file_from_docker(docker_link, api_function_calls, apis_args, gpu_type):
    api_file_path = os.path.join(os.getcwd(), "modal_apis.py")

    api_function_names = ["_".join(func.split('.')) for func in api_function_calls]

    content = f"""import json
import modal

stub = modal.Stub()
docker_img = modal.Image.from_registry("{docker_link}")

"""
    for i in range(len(api_function_calls)):
        api_args = apis_args[api_function_calls[i]]
        content += get_api_func_signature(api_function_names[i], api_function_calls[i], api_args, img="docker_img", gpu=gpu_type)

    with open(api_file_path, 'w') as file:
        file.write(content)

def get_api_links(apis):
    apis = ["-".join(s.split('.')) for s in apis]
    apis = ["-".join(s.split("_")) for s in apis]
    apis = [s.lower() for s in apis]
    api_links = [f"https://kcui5--modal-apis-py-{s}-dev.modal.run" for s in apis]
    return api_links

def serve_apis(conda_env_name, apis):
    try:
        api_file_path = "modal_apis.py"
        serve_command = f"conda run --name {conda_env_name} modal serve {api_file_path}"
        print(get_api_links(apis))
        subprocess.run(serve_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error serving APIs: ", e)
        exit()
