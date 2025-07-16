### Implementation Proposal

To resolve this Issue, I will proceed with the implementation according to the following plan.

**Files to be changed:**
- `src/ocr_poc.py` (Verification, no major changes expected)
- `tests/test_ocr_poc.py` (New file for basic test)
- `README.md` or `docs/04_SETUP.md` (Basic usage instructions, if necessary)

#### 1. **Contribution to Project Goals**
この変更は、`SDD.md`で定義されている開発ロードマップの「Sprint 1: PDF → image → PP‑OCRv5 CLI PoC」を完了させ、プロジェクトの主要なOCR機能の概念実証を確立します。

#### 2. **Overview of Changes**
既存の`src/ocr_poc.py`が`SDD.md`の要件（PDFから画像への変換、PP-OCRv5によるOCR、指定されたCSVフォーマットでの出力、`--no-csv`および`--zip`オプション）を既に満たしていることを確認します。その後、CLIからの実行とCSV出力の基本的な動作を検証するためのシンプルなテストケースを追加します。必要に応じて、`README.md`または`docs/04_SETUP.md`に基本的な使用方法を追記します。

#### 3. **Specific Work Content for Each File**
- `src/ocr_poc.py`: コードのレビューと、`SDD.md`の要件との最終的な整合性確認を行います。機能的な変更はほとんど、あるいは全く必要ないと予想されます。
- `tests/test_ocr_poc.py`:
    - `src/ocr_poc.py`をCLIとして実行するテストケースを作成します。
    - サンプルPDFファイル（例: `tests/test.pdf`）を入力として使用します。
    - OCR結果のCSVファイルが正しく生成され、指定されたカラム（`page`, `block_id`, `x0`, `y0`, `x1`, `y1`, `text`, `confidence`）が含まれていることを確認します。
    - オプションで、`--zip`フラグを使用した際のZIPファイルの生成も確認します。
- `README.md` or `docs/04_SETUP.md`: `src/ocr_poc.py`のCLIとしての基本的な実行方法（例: `python src/ocr_poc.py <pdf_path>`）を追記します。

#### 4. **Definition of Done**
- [ ] All necessary code changes have been implemented (or verified as already implemented).
- [ ] New tests have been added to cover the changes (a basic test for CLI execution and CSV output).
- [ ] All existing and new tests pass.
- [ ] The documentation has been updated to reflect the changes (basic usage in README/docs).
- [ ] The implementation has been manually verified.

---
If you approve, please reply to this comment with "Approve".