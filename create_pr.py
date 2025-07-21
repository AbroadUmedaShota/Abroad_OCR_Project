
import subprocess

base_branch = "main"
head_branch = "5-implement-pdf-to-image-and-pp-ocr-v5-cli-poc"
title = "feat: Implement PDF to image and PP-OCRv5 CLI PoC"
body_file = "C:/Users/OFFI/Desktop/WorkSpace/00.dev/Abroad_OCR_Project/pr_body.txt"

command = ["gh", "pr", "create", "--base", base_branch, "--head", head_branch, "--title", title, "--body-file", body_file]

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)
except subprocess.CalledProcessError as e:
    print("Error:", e)
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)
