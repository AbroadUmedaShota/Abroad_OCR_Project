import subprocess

label_name = "status: implementing"
color = "1D76DB"
description = "State where the AI is in the process of implementation"

command = ["gh", "label", "create", label_name, "--color", color, "--description", description]

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)
except subprocess.CalledProcessError as e:
    print("Error:", e)
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)