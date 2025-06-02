import re

app_py_path = 'app.py'

with open(app_py_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# ---- 1. Add Imports ----
# Define the imports that are definitely needed for the admin functionality.
# json is already there from a previous step.
required_imports_set = {
    "from flask import Blueprint, render_template, redirect, url_for, flash, request",
    "from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user",
    "from werkzeug.security import generate_password_hash, check_password_hash",
    "import os"
}

# Find existing imports to avoid duplication and merge flask imports
existing_flask_imports = set()
new_flask_import_names = {"Blueprint", "render_template", "redirect", "url_for", "flash", "request"}

# Remove flask import from required_imports_set to handle it separately
flask_import_line_template = "from flask import {imports}"
required_imports_set.discard("from flask import Blueprint, render_template, redirect, url_for, flash, request")

# Find existing "from flask import ..."
flask_import_match = re.search(r"^from flask import .+$", app_content, re.MULTILINE)
if flask_import_match:
    current_flask_import_line = flask_import_match.group(0)
    imported_names_match = re.search(r"from flask import (.*)", current_flask_import_line)
    if imported_names_match:
        names_str = imported_names_match.group(1)
        # Handle cases like 'Flask, render_template as rt' - keep original if complex, otherwise just names
        if ' as ' not in names_str: # Simple case
            existing_flask_imports.update([name.strip() for name in names_str.split(',')])

    # Add new names if they are not already there
    new_flask_import_names.update(existing_flask_imports)
    updated_flask_names_str = ", ".join(sorted(list(new_flask_import_names)))
    updated_flask_import_line = flask_import_line_template.format(imports=updated_flask_names_str)

    # Replace the old flask import line
    app_content = app_content.replace(current_flask_import_line, updated_flask_import_line)
else:
    # If no "from flask import ..." line, add the full new one.
    required_imports_set.add(flask_import_line_template.format(imports=", ".join(sorted(list(new_flask_import_names)))))

# Add other required imports if not found (simple check)
imports_to_add_at_end_of_block = []
for imp_line in required_imports_set:
    # Basic check: if the main module (e.g. flask_login, os) is mentioned.
    module_name = imp_line.split(" ")[1].split(".")[0] # e.g. "flask_login" from "from flask_login import X" or "os" from "import os"
    if not re.search(r"import\s+" + re.escape(module_name) + r"|from\s+" + re.escape(module_name) + r"\s+import", app_content):
        imports_to_add_at_end_of_block.append(imp_line)

# Find the last import line to append these new imports
last_import_pos = 0
for match in re.finditer(r"^(?:from\s+.+\s+import\s.+|import\s.+)$", app_content, re.MULTILINE):
    last_import_pos = match.end()

if imports_to_add_at_end_of_block:
    if last_import_pos > 0:
        app_content = app_content[:last_import_pos] + "\n" + "\n".join(imports_to_add_at_end_of_block) + app_content[last_import_pos:]
    else: # Prepend to beginning if no imports found at all (unlikely for flask app)
        app_content = "\n".join(imports_to_add_at_end_of_block) + "\n" + app_content
print("Imports check/update complete.")

# ---- 2. Insert Admin Setup Code (User class, LoginManager instance, Blueprint routes) ----
with open('admin_setup_changes.py', 'r', encoding='utf-8') as f:
    admin_code_raw = f.read()

# Remove the temporary import lines from admin_setup_changes.py as they are handled above
admin_code = "\n".join([line for line in admin_code_raw.splitlines() if not line.strip().startswith(("from ", "import "))])
admin_code = "\n# ---- Admin Setup ----\n" + admin_code

# Insert admin_code before the first @app.cli.command or if __name__ == '__main__'
# This ensures models are defined before these are used by CLI or routes.
# And LoginManager is defined before being initialized.
cli_command_marker = "@app.cli.command('init-db')"
first_route_marker = "@app.route('/')"

insertion_point = -1

# Prefer to insert before CLI commands
if cli_command_marker in app_content:
    insertion_point = app_content.find(cli_command_marker)
    print(f"Found CLI command marker. Inserting admin setup code before it at position {insertion_point}.")
# Else, before the first main application route
elif first_route_marker in app_content:
    insertion_point = app_content.find(first_route_marker)
    print(f"Found first app route marker. Inserting admin setup code before it at position {insertion_point}.")
else:
    # Fallback: if no CLI and no main routes, try before 'if __name__ == "__main__"'
    main_exec_marker = "if __name__ == '__main__':"
    if main_exec_marker in app_content:
        insertion_point = app_content.find(main_exec_marker)
        print(f"Found main execution marker. Inserting admin setup code before it at position {insertion_point}.")
    else:
        insertion_point = len(app_content) # Append if no other markers found (less ideal)
        print(f"No suitable marker found. Appending admin setup code to end (position {insertion_point}).")

app_content = app_content[:insertion_point] + admin_code + "\n\n" + app_content[insertion_point:]
print("Admin setup code (User class, LoginManager, blueprint routes) inserted.")


# ---- 3. Add SECRET_KEY update and LoginManager initialization ----
# This block needs to be *after* 'app = Flask(__name__)' and after 'login_manager = LoginManager()'
# It's part of the admin_setup_changes.py conceptually.
app_init_marker = "app = Flask(__name__)"
app_init_pos = app_content.find(app_init_marker)

secret_key_init_code = """
# Ensure app config has a decent secret key for Flask-Login
if not app.config.get('SECRET_KEY') or app.config.get('SECRET_KEY') == 'your_secret_key':
    print("WARNING: Using a default or weak SECRET_KEY. Generating a new one for this session.")
    app.config['SECRET_KEY'] = os.urandom(24).hex()

# Initialize Flask-Login with the app instance
login_manager.init_app(app)
"""
if app_init_pos != -1:
    # Find end of that line
    end_of_app_init_line = app_content.find("\n", app_init_pos)
    if end_of_app_init_line != -1:
        # Insert after the app = Flask(__name__) line
        app_content = app_content[:end_of_app_init_line+1] + secret_key_init_code + app_content[end_of_app_init_line+1:]
        print("SECRET_KEY check and login_manager.init_app(app) inserted after app initialization.")
    else: # app = Flask(__name__) is the last line
        app_content += secret_key_init_code
        print("SECRET_KEY check and login_manager.init_app(app) appended (app init was last line).")
else:
    print("ERROR: 'app = Flask(__name__)' not found. Could not insert SECRET_KEY and LoginManager init logic.")


# ---- 4. Register the blueprint ----
# This should be done after blueprint ('admin_bp') is defined and 'app' is defined,
# but before the app is run. Usually towards the end of file, before 'if __name__ == "__main__"'.
blueprint_registration = "\napp.register_blueprint(admin_bp)\n"
main_exec_marker = "if __name__ == '__main__':"

if main_exec_marker in app_content:
    insertion_point_bp = app_content.find(main_exec_marker)
    app_content = app_content[:insertion_point_bp] + blueprint_registration + "\n" + app_content[insertion_point_bp:]
    print(f"Admin blueprint registered before '{main_exec_marker}'.")
else:
    app_content += blueprint_registration # Append if no main_exec_marker
    print(f"Admin blueprint registered at the end of the file.")


with open(app_py_path, 'w', encoding='utf-8') as f:
    f.write(app_content)

print("app.py modified for admin setup.")
