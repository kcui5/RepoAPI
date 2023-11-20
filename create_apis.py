import os

def get_api_func_signature(repo_name, func_name, func_call):
    content = f"""@stub.function(mounts=[modal.Mount.from_local_python_packages("{repo_name}")])
@modal.web_endpoint()
def {func_name}():
    return {repo_name}.{func_call}()
    
"""
    return content

def create_api_file(repo_name, api_function_calls):
    api_file_path = os.path.join(os.getcwd(), "modal_apis.py")

    api_function_names = ["_".join(func.split('.')) for func in api_function_calls]

    content = f"""import modal
import {repo_name}

stub = modal.Stub()

"""
    for i in range(len(api_function_calls)):
        content += get_api_func_signature(repo_name, api_function_names[i], api_function_calls[i])
    
    with open(api_file_path, 'w') as file:
        file.write(content)
