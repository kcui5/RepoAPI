import os
import glob

def fix_imports(path):
    with open(path, 'r') as file:
            # Read the contents of the file
            contents = file.read()

            # Process the contents here
            print(f"Processing {file_path}...")
            # Example: print the contents
            print(contents)

def recursively_fix_imports(subfolder):
    """
    Fixes import statements for all Python files in the specified subfolder.

    Args:
    subfolder (str): The name of the subfolder.
    """
    # Create the path to the subfolder
    subfolder_path = os.path.join(os.getcwd(), subfolder)

    # Find all Python files in the subfolder
    python_files = glob.glob(os.path.join(subfolder_path, '*.py'))

    # Process each Python file
    for file_path in python_files:
        fix_imports(file_path)
        

