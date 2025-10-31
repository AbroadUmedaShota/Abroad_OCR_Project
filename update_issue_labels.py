import subprocess

issue_number = "22"
remove_label = "status: planning"
add_labels = ["status: implementing"]

command = [
    "gh", "issue", "edit", issue_number,
    "--add-assignee", "@me"
]

for label in add_labels:
    command.extend(["--add-label", label])

if remove_label:
    command.extend(["--remove-label", remove_label])

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(f"Successfully updated labels for issue #{issue_number}")
    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)
except subprocess.CalledProcessError as e:
    print("Error:", e)
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)