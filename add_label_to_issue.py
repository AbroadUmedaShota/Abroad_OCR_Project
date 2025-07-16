
import subprocess

issue_number = 5
label_name = "status: planning"

command = ["gh", "issue", "edit", str(issue_number), "--add-label", label_name]

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)
except subprocess.CalledProcessError as e:
    print("Error:", e)
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)
