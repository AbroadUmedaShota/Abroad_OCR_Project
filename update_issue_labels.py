import subprocess

issue_number = "8"
remove_label = "status: review"
add_label = "status: done"

command = [
    "gh", "issue", "edit", issue_number,
    "--remove-label", remove_label,
    "--add-label", add_label
]

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(f"Successfully updated labels for issue #{issue_number}")
    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)
except subprocess.CalledProcessError as e:
    print("Error:", e)
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)