import os
import subprocess
import re

def security_check_repo(repo_path):
    """Checks repository for any dangerous code"""
    dangerous = {' subprocess', ' os', ' eval', ' exec', ' sys', ' shutil', ' socket', ' ctypes', ' pickle', ' compile', ' open', ' importlib', ' __import__', ' platform', ' inspect'}
    
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path) as f:
                for line in f:
                    if any(dangerous_word in line for dangerous_word in dangerous):
                        return False
    return True

def get_python_modules(directory):
    """Returns a set of all Python module names in the directory, including subdirectories."""
    module_names = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                # Construct module name from file name
                module_name = file[:-3]
                module_names.add(module_name)
    return module_names

def get_external_packages(directory):
    """Reads the requirements.txt file and returns a list of packages."""
    packages = set()
    requirements_path = os.path.join(directory, "requirements.txt")
    if not os.path.exists(requirements_path):
        return "No requirements.txt file!"

    with open(requirements_path, 'r') as file:
        for line in file:
            # Remove whitespace and skip comments and empty lines
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle lines with package version specifiers
                package = line.split('==')[0].strip()
                packages.add(package)
    return packages

def fix_imports(file_path, pkg_name, local_modules, external_packages):
    #TO HANDLE SPECIAL CASE OF TORCH PACKAGE NOT BEING IN REQUIREMENTS.TXT:
    external_packages.add("torch")

    print(f"Fixing imports in... {file_path}")
    with open(file_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        # Check if the line is an import statement
        stripped_line = line.lstrip()
        if stripped_line.startswith('import ') or stripped_line.startswith('from '):
            # Determine if the import is local or external
            is_local = any(local_module in line for local_module in local_modules)
            is_external = any(external_pkg in line for external_pkg in external_packages)

            # Update the import statement
            if is_local:
                if is_external:
                    print(f"Unrecognized local and external package from line: {line}!")
                    new_line = line
                else:
                    # Modify line to use local package import
                    if stripped_line.startswith('import ') and not stripped_line.startswith('import .'):
                        new_line = line.replace('import ', 'from . import ', 1)
                    elif stripped_line.startswith('from ') and not stripped_line.startswith('from .'):
                        new_line = line.replace('from ', f'from {pkg_name}.', 1)
                    else:
                        new_line = line
                    if line != new_line:
                        print(f"Replacing {line} with {new_line}!")
                new_lines.append(new_line)
            elif is_external:
                # Leave external imports as they are
                new_lines.append(line)
            else:
                #print(f"Unrecognized package from line: {line}!")
                new_lines.append(line)
        else:
            new_lines.append(line)

    # Write the updated lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(new_lines)

def recursively_fix_imports(repo_path, repo_name):
    """
    Fixes import statements for all Python files in the specified subfolder.

    Args:
    repo_path (os.path): The path to the repository.
    repo_name (str): The name of the repository.
    """
    local_modules = get_python_modules(repo_path)
    external_packages = get_external_packages(repo_path)
    if type(external_packages) == str:
        return external_packages
    
    # Process each file in the local package
    for root, dirs, files in os.walk(repo_path):
        for name in files:
            if name.endswith('.py'):
                if name == "setup.py":
                    print("Skipping setup.py file!")
                    continue
                fix_imports(os.path.join(root, name), repo_name, local_modules, external_packages)
    return "Fixed imports!"
        
def fix_argparse(file, func_name, func_args):
    """Converts argparse inputted arguments into function signature arguments
    file is the file being fixed
    args is a list of args (the value in the key-value pair of args dict)
    
    Does not support arguments set with dest= in .add_argument()!!
    Does not support fixing functions who already take in arguments with default values in addition to argparse arguments!!"""
    print(f"Fixing argparse in {file}...")
    with open(file, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    #Object set to the argparse.ArgumentParser().parse_args() object (which holds all the args as attributes)
    parser_parse_args_obj_pattern = r'\b(\w+)\s*=\s*(\w+)\.parse_args\(\)'
    parser_parse_args_obj = ""
    for line in lines:
        new_line = ""
        if f"def {func_name}" in line:
            previous_func_args = re.findall(r'\((.*?)\)', line)
            if len(previous_func_args) > 1:
                print("Unrecognized function declaration:")
                print(line)
                exit()
            if previous_func_args == ['']:
                args_str = '(' + ", ".join(func_args) + ')'
            else:
                new_func_args = []
                previous_func_args_items = [a.strip() for a in previous_func_args[0].split(",")]
                for a in func_args:
                    if a not in previous_func_args_items:
                        new_func_args.append(a)
                if new_func_args:
                    args_str = '(' + previous_func_args[0] + ", " + ", ".join(new_func_args) + ')'
                else:
                    args_str = '(' + previous_func_args[0] + ')'
            new_line = line.replace(f'({previous_func_args[0]})', args_str)
        elif ".add_argument(" in line:
            new_line = "#" + line
            #Does not check for dest= being set !!
        elif re.search(parser_parse_args_obj_pattern, line):
            parser_parse_args_obj = line[:line.find(" =")].lstrip()
            print(f"Found parser_parse_args_obj {parser_parse_args_obj}")
            new_line = "#" + line
        elif parser_parse_args_obj and parser_parse_args_obj in line:
            new_line = line.replace(parser_parse_args_obj + ".", "")
        else:
            new_line = line
        if line != new_line:
            print(f"Replacing {line} with {new_line}!")
        new_lines.append(new_line)
    with open(file, 'w') as f:
        f.writelines(new_lines)

def fix_all_argparse(repo_path, apis, apis_args):
    for i in range(len(apis)):
        file = os.path.join(repo_path, '.'.join(apis[i].split('.')[:-1])+'.py')
        with open(file, 'r') as f:
            for line in f:
                if "argparse" in line:
                    fix_argparse(file, apis[i].split('.')[-1], apis_args[apis[i]])
                    break

def create_init_file(repo_path, api_functions):
    init_file_path = os.path.join(repo_path, "__init__.py")
    import_files = set()
    for func in api_functions:
        chain = func.split('.')[:-1]
        if len(chain) == 1:
            file = f"from . import {chain[0]}"
        elif len(chain) == 2:
            file = f"from .{chain[0]} import {chain[1]}"
        elif len(chain) > 2:
            file = "from " + ".".join(chain[:-1]) + f" import {chain[-1]}"
        import_files.add(file)
    file_import_string = "\n".join(import_files)

    with open(init_file_path, 'w') as file:
        file.write(file_import_string)

def create_setup_file(repo_name):
    setup_file_path = os.path.join(os.getcwd(), repo_name, "setup.py")

    with open(setup_file_path, 'w') as file:
        content = f"""from setuptools import setup, find_packages

setup(
    name='{repo_name}',
    version='0.1.0',
    package_dir={{"": "src"}},
    packages=find_packages(where="src"),
    include_package_data=True,
    description='A module to upload to modal',
    install_requires=[
    
    ],
)
"""
        file.write(content)

def create_manifest_file(repo_name):
    manifest_file_path = os.path.join(os.getcwd(), repo_name, "MANIFEST.in")
    with open(manifest_file_path, 'w') as file:
        file.write("graft src")

def pip_install_packages():
    pkg_file_path = os.path.join("/root", "package")
    try:
        """subprocess.run('ls -a', shell=True, check=True)
        subprocess.run('echo $PATH', shell=True, check=True)
        subprocess.run('echo \'export PATH="/root/.local/bin:$PATH"\' >> ~/.bashrc', shell=True, check=True)
        subprocess.run('echo \'export PATH="/root/.local/bin:$PATH"\' >> ~/.profile', shell=True, check=True)
        subprocess.run('echo $PATH', shell=True, check=True)
        subprocess.run(f"pip install --user --force-reinstall modal", shell=True, check=True)"""
        subprocess.run("pip install virtualenv", shell=True, check=True)
        print("Installed virtualenv")
        subprocess.run("virtualenv /pkgsvenv", shell=True)
        activate_command = "source /pkgsvenv/bin/activate"
        modal_install_command = "pip install modal"
        subprocess.run(f"{activate_command} && {modal_install_command}", shell=True, executable="/bin/bash")
        print(f"Successfully pip installed modal")
        pkg_install_command = f"pip install {pkg_file_path}"
        subprocess.run(f"{activate_command} && {pkg_install_command}", shell=True, check=True, executable="/bin/bash")
        print("Local package pip installed successfully.")

    except subprocess.CalledProcessError as e:
        print("Error installing package:", e)
        exit()

def conda_install_packages(conda_env_name, repo_name):
    try:
        subprocess.run(f"conda create --name {conda_env_name} --yes", shell=True, check=True)
        print(f"Conda environment {conda_env_name} created successfully")
    except subprocess.CalledProcessError as e:
        return f"Error creating environment: {e}"

    pkg_file_path = os.path.join(os.getcwd(), repo_name)
    try:
        subprocess.run(f"conda run --name {conda_env_name} pip install modal", shell=True, check=True)
        print(f"Successfully installed modal in {conda_env_name}")
        install_command = f"conda run --name {conda_env_name} pip install {pkg_file_path}"
        subprocess.run(install_command, shell=True, check=True)
        print("Local package installed successfully.")
        return f"Installed local package into conda env {conda_env_name}"
    except subprocess.CalledProcessError as e:
        return f"Error installing package: {e}"
    
def venv_install_packages(venv_name, repo_name):
    try:
        subprocess.run(f"python -m venv {venv_name}", shell=True, check=True)
        print(f"Virtual environment '{venv_name}' created.")
    except subprocess.CalledProcessError as e:
        return f"Error creating venv: {e}"
    """
    pkg_file_path = os.path.join(os.getcwd(), repo_name)
    pip_executable = os.path.join(venv_name, "bin", "pip")
    try:
        subprocess.run(f"{pip_executable} install modal", shell=True, check=True)
        print(f"Successfully installed modal in {venv_name}")
        subprocess.run(f"{pip_executable} install {pkg_file_path}", shell=True, check=True)
        print(f"Successfully installed local package in {venv_name}")
        return f"Installed local package into venv {venv_name}"
    except subprocess.CalledProcessError as e:
        return f"Error installing package: {e}"""

def clean_state():
    try:
        #subprocess.run(f"conda env remove --name {conda_env_name}")
        p = os.path.join(os.getcwd(), "package")
        np = os.path.join(os.getcwd(), "old_package")
        subprocess.run(f"mv {p} {np}")
    except subprocess.CalledProcessError as e:
        print("Error cleaning state: ", e)

venv_install_packages("pd_modal_venv", "pd_modal")
