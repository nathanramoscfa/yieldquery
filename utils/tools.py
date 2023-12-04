import os


def find_project_root(current_dir):
    """
    Traverses up from the current directory until it finds the project root directory.
    The root is identified by the presence of a .git directory or setup.py file.
    """
    while current_dir != os.path.dirname(current_dir):  # Check until the root of the directory tree
        if os.path.exists(os.path.join(current_dir, '.git')) or os.path.exists(os.path.join(current_dir, 'setup.py')):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    raise FileNotFoundError("Project root directory not found.")
