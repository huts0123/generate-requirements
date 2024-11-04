import ast
import pkg_resources
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os

def extract_imports_from_file(file_path):
    """ Extract import statements from a Python file. """
    try:
        with open(file_path, 'r') as file:
            node = ast.parse(file.read(), filename=file_path)

        imports = set()
        for n in ast.walk(node):
            if isinstance(n, ast.Import):
                for alias in n.names:
                    imports.add(alias.name)
            elif isinstance(n, ast.ImportFrom):
                imports.add(n.module)

        return imports
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return set()

def get_requirements(imports):
    """ Map imported modules to their package names and versions. """
    requirements = set()
    for module in imports:
        try:
            dist = pkg_resources.get_distribution(module)
            requirements.add(f"{dist.project_name}=={dist.version}")
        except pkg_resources.DistributionNotFound:
            requirements.add(module)  # Use the module name if not found
    return requirements

def generate_unique_filename(base_name, extension):
    """ Generate a unique filename by appending a number if needed. """
    counter = 0
    filename = f"{base_name}{extension}"
    while os.path.exists(filename):
        counter += 1
        filename = f"{base_name}{counter}{extension}"
    return filename

def write_requirements_to_file(requirements, base_name='requirements', extension='.txt'):
    """ Write requirements to a file with a unique name. """
    output_file = generate_unique_filename(base_name, extension)
    try:
        with open(output_file, 'w') as file:
            for requirement in sorted(requirements):
                file.write(f"{requirement}\n")
        return output_file
    except Exception as e:
        print(f"Error writing to file: {e}")
        return None

def process_file(file_path):
    """ Process the dropped Python file to extract imports and write requirements. """
    imports = extract_imports_from_file(file_path)
    requirements = get_requirements(imports)
    output_file = write_requirements_to_file(requirements)
    return output_file

def drop(event):
    """ Handle the drop event for the file. """
    file_path = event.data.strip('{}')  # Clean up the dropped file path
    if os.path.isfile(file_path) and (file_path.endswith('.py') or file_path.endswith('.pyw')):
        output_file = process_file(file_path)
        if output_file:
            result_label.config(text=f"Requirements written to {output_file}")
        else:
            result_label.config(text="Error writing requirements.")
    else:
        result_label.config(text="Please drop a valid .py or .pyw file.")

# Create the GUI
root = TkinterDnD.Tk()
root.title("Dependency Extractor")
root.geometry("400x200")

# Create a label for instructions
label = tk.Label(root, text="Drag and drop your .py or .pyw file here", padx=10, pady=10)
label.pack(expand=True)

# Create a label to show results
result_label = tk.Label(root, text="", padx=10, pady=10)
result_label.pack(expand=True)

# Configure drag-and-drop
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)

# Add a button for installation instructions
import tkinter.messagebox as messagebox

def show_instructions():
    instructions = (
        "To install the requirements from requirements.txt:\n"
        "1. Open your command prompt or terminal.\n"
        "2. Navigate to the directory where requirements.txt is located:\n"
        "   cd path\\to\\your\\directory\n"
        "3. Run the following command:\n"
        "   pip install -r requirements.txt\n"
    )
    messagebox.showinfo("Installation Instructions", instructions)

# Create a button for installation instructions
instructions_button = tk.Button(root, text="Show Installation Instructions", command=show_instructions)
instructions_button.pack(pady=10)

# Start the GUI event loop
root.mainloop()
