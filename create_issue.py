
import subprocess

title = "feat: Implement PDF to image and PP-OCRv5 CLI PoC"
body = """このIssueでは、PDFファイルを画像に変換し、その画像に対してPP-OCRv5を用いたOCR処理をCLIから実行できる概念実証（PoC）を実装します。OCR結果はCSV形式で出力されるようにします。

具体的には、以下の作業を行います。

*   PDFファイルをページごとに画像に変換する機能の実装。
*   変換された画像に対してPaddleOCR（PP-OCRv5）を実行し、テキストを抽出する機能の実装。
*   CLIからPDFファイルのパスを受け取り、OCR処理を実行できるインターフェースの作成。
*   OCR結果を`SDD.md`の「3.4 出力形式」に定義されているCSVフォーマット（`page`, `block_id`, `x0`, `y0`, `x1`, `y1`, `text`, `confidence`）で出力する機能の実装。
*   既存の`src/ocr_poc.py`をベースに開発を進めます。"""

command = ["gh", "issue", "create", "--title", title, "--body", body]

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)
except subprocess.CalledProcessError as e:
    print("Error:", e)
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)
