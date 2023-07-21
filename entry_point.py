import main as my_module
import os
import glob

CURRENT_DIR = os.path.dirname(__file__)

# Function to find all Python files (modules) within a package
def find_modules(package_path):
    return glob.glob(os.path.join(package_path, "*.py"))

# Function to generate hidden imports for all packages and modules
def generate_hidden_imports(root_dir):
    hidden_imports = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if "__init__.py" in filenames:
            package_path = os.path.relpath(dirpath, root_dir).replace(os.sep, ".")
            modules = find_modules(dirpath)
            hidden_imports.extend([f"{package_path}.{os.path.splitext(os.path.basename(module))[0]}" for module in modules])
    print(hidden_imports)
    return hidden_imports

# Function to write hidden imports to the hidden-import.txt file
def write_hidden_imports_to_file(hidden_imports, file_path):
    with open(file_path, "w") as file:
        file.write(str(hidden_imports))

# Write the hidden imports to the hidden-import.txt file
hidden_imports = generate_hidden_imports(CURRENT_DIR)
hidden_imports_file = "hidden-import.txt"
# write_hidden_imports_to_file(hidden_imports, hidden_imports_file)

if __name__ == '__main__':
    my_module.main()