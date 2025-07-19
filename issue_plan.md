### Implementation Proposal

To resolve this Issue, I will proceed with the implementation according to the following plan.

**Files to be changed:**
- `src/ocr_poc.py`
- `requirements.txt`
- `tests/test_ocr_poc.py` (new file)

#### 1. **Contribution to Project Goals**
- This change implements the core OCR processing PoC defined as the goal for Sprint 1 in the `SDD.md`, establishing the foundation for subsequent development.

#### 2. **Overview of Changes**
- Based on the existing `src/ocr_poc.py`, I will refine the script to focus solely on the requirements of this issue: converting a PDF to images, performing OCR, and outputting the results to a CSV file. I will remove functionality that is out of scope for this PoC, such as creating searchable PDFs.

#### 3. **Specific Work Content for Each File**
- `src/ocr_poc.py`:
    - Remove the `create_searchable_pdf` function and the `zipfile` import as they are not within the scope of this issue.
    - Modify the `main` function to remove the call to `create_searchable_pdf` and the associated `--zip` argument processing.
    - Remove the debug file output from the `run_ocr` function to clean up the code.
- `requirements.txt`:
    - Ensure that all necessary libraries (`paddleocr`, `PyMuPDF`, `Pillow`) are listed.
- `tests/test_ocr_poc.py`:
    - Create a new test file.
    - Add a unit test for the `pdf_to_images` function.
    - Add a unit test for the `run_ocr` function.
    - A sample PDF file for testing will be placed in the `tests/` directory.

#### 4. **Definition of Done**
- [ ] All necessary code changes have been implemented.
- [ ] New tests have been added to cover the changes.
- [ ] All existing and new tests pass.
- [ ] The documentation has been updated to reflect the changes.
- [ ] The implementation has been manually verified.

---
If you approve, please reply to this comment with "Approve".
