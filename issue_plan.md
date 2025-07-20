### Implementation Proposal

To resolve this Issue, I will proceed with the implementation of the IoU Check feature according to the following plan. I propose to split the Tauri UI Alpha implementation into a separate, future issue due to its distinct technology stack and complexity.

**Files to be changed:**
- `scripts/calculate_iou.py` (new file)
- `src/ocr_poc.py`
- `tests/test_ocr_poc.py`
- `SDD.md`
- `docs/00_PROJECT_OVERVIEW.md`
- `docs/01_ARCHITECTURE.md`

#### 1. **Contribution to Project Goals**
- This change implements the framework for IoU checking, which is crucial for evaluating the quality of bounding box detection, a key quality requirement in `SDD.md`.

#### 2. **Overview of Changes**
- I will implement a utility function for IoU calculation and integrate a placeholder for its use within `src/ocr_poc.py`. The test suite will be extended to verify the IoU calculation.

#### 3. **Specific Work Content for Each File**
- `scripts/calculate_iou.py`:
    - Create a new Python file containing a function to calculate IoU between two bounding boxes.
- `src/ocr_poc.py`:
    - Add a placeholder for IoU calculation within `run_ocr`, where OCR-detected bounding boxes would be compared against ground truth (when available).
- `tests/test_ocr_poc.py`:
    - Add new test cases to verify the correctness of the `calculate_iou` function using various bounding box scenarios.
- `SDD.md`:
    - Update sections `3.2 品質要件` (Bounding Box IoU) and `9. テスト計画` (IoU testing methodology) to reflect the implementation.
- `docs/00_PROJECT_OVERVIEW.md`:
    - Update `3. 主要機能 (Proof of Concept)` to mention the inclusion of the IoU check framework.
- `docs/01_ARCHITECTURE.md`:
    - Update relevant sections to reflect the IoU check implementation.

#### 4. **Definition of Done**
- [ ] All necessary code changes have been implemented.
- [ ] New tests have been added to cover the changes.
- [ ] All existing and new tests pass.
- [ ] The documentation has been updated to reflect the changes.
- [ ] The implementation has been manually verified.

---
If you approve, please reply to this comment with "Approve".
