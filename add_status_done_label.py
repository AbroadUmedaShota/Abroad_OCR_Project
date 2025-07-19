
import subprocess

label_name = "status: done"
color = "0E8A16"
description = "State where the Issue has been addressed and merged"

command = ["gh", "label", "create", label_name, "--color", color, "--description", description]

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print("Successfully created label:", label_name)
    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)
except subprocess.CalledProcessError as e:
    # If the label already exists, the command will fail. We can ignore this error.
    if "already exists" in e.stderr:
        print("Label already exists:", label_name)
    else:
        print("Error:", e)
        print("Stdout:", e.stdout)
        print("Stderr:", e.stderr)
