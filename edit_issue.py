
import subprocess

issue_number = "8"
assignee = "@me"
labels = ["type: feature", "status: planning"]

command = ["gh", "issue", "edit", issue_number, "--add-assignee", assignee]
for label in labels:
    command.extend(["--add-label", label])

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(f"Successfully edited issue #{issue_number}")
    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)
except subprocess.CalledProcessError as e:
    print("Error:", e)
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)
