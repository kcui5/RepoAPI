import os

def get_python_modules(directory):
    """ Returns a set of all Python module names in the directory, including subdirectories. """
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

    with open(requirements_path, 'r') as file:
        for line in file:
            # Remove whitespace and skip comments and empty lines
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle lines with package version specifiers
                package = line.split('==')[0].strip()
                packages.add(package)
    return packages

def fix_imports(file_path, local_modules, external_packages):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        # Check if the line is an import statement
        if line.startswith('import ') or line.startswith('from '):
            # Determine if the import is local or external
            is_local = any(local_module in line for local_module in local_modules)
            is_external = any(external_pkg in line for external_pkg in external_packages)

            # Update the import statement
            if is_local:
                if is_external:
                    print(f"Unrecognized package from line {line}!")
                else:
                    # Modify line to use local package import
                    if line.startswith('import '):
                        new_line = line.replace('import ', 'from . import ', 1)
                    elif line.startswith('from '):
                        new_line = line.replace('from ', 'from .', 1)
                    new_lines.append(new_line)
            elif is_external:
                # Leave external imports as they are
                new_lines.append(line)
            else:
                print(f"Unrecognized package from line {line}!")
        else:
            new_lines.append(line)

    # Write the updated lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(new_lines)

def recursively_fix_imports(subfolder):
    """
    Fixes import statements for all Python files in the specified subfolder.

    Args:
    subfolder (str): The name of the subfolder.
    """
    # Create the path to the subfolder
    subfolder_path = os.path.join(os.getcwd(), subfolder)
    local_modules = get_python_modules(subfolder_path)
    external_packages = get_external_packages(subfolder_path)

    # Process each file in the local package
    for root, dirs, files in os.walk(subfolder_path):
        for name in files:
            if name.endswith('.py'):
                fix_imports(os.path.join(root, name), local_modules, external_packages)
        

