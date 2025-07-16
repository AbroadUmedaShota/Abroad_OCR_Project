
import subprocess

issue_number = 5
remove_label = "status: planning"
add_label = "status: implementing"

command = ["gh", "issue", "edit", str(issue_number), "--remove-label", remove_label, "--add-label", add_label]

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)
except subprocess.CalledProcessError as e:
    print("Error:", e)
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)
