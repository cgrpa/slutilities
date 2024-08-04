import os

def print_directory_tree(startpath, ignore_dirs=None, indent=''):
    if ignore_dirs is None:
        ignore_dirs = []
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_dirs]
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{sub_indent}{f}")
        for d in dirs:
            print_directory_tree(os.path.join(root, d), ignore_dirs, sub_indent)

# Replace 'your_project_directory' with the path to your project directory
start_path = './'
ignore_dirs = [os.path.join(start_path, 'venv'),os.path.join(start_path, '.git')]  # Add any other directories to ignore here

print_directory_tree(start_path, ignore_dirs)