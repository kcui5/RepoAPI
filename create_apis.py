import os
import subprocess
import json

def get_api_func_signature(repo_name, func_name, func_call):
    res_string = """res_json = {
        "status": "200",
        "data": {
            "res": f'{res}'
        }
    }
"""
    content = f"""@stub.function(mounts=[modal.Mount.from_local_python_packages("{repo_name}")])
@modal.web_endpoint()
def {func_name}():
    res = {repo_name}.{func_call}()
    {res_string}
    print(res_json)
    res_json = json.dumps(res_json)
    return res_json
"""
    return content

def create_api_file(repo_name, api_function_calls):
    api_file_path = os.path.join(os.getcwd(), "modal_apis.py")

    api_function_names = ["_".join(func.split('.')) for func in api_function_calls]

    content = f"""import json
import modal
import {repo_name}

stub = modal.Stub()

"""
    for i in range(len(api_function_calls)):
        content += get_api_func_signature(repo_name, api_function_names[i], api_function_calls[i])
    
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
        print("Serving APIs on Modal...")
        print(get_api_links(apis))
        process = subprocess.run(serve_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error serving APIs: ", e)
        exit()
