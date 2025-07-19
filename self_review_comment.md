### Self-Review Report

I have conducted a self-review and confirmed that the implementation aligns with the project's standards and the requirements of the Issue. All standard checks, including diff confirmation, convention adherence, and documentation updates, have been successfully passed.

---

### Quality Gate Assessment

- **Computational Complexity:** The integration of DBNet++ for detection and separate recognition steps might introduce some overhead compared to a single `ocr.ocr` call, but it allows for more granular control and potential future optimizations. For a PoC, this is acceptable.
- **Security:** The changes primarily involve integrating a new component (DBNet++) within the existing offline OCR pipeline. No new external dependencies or network communications are introduced that would compromise the offline security posture.
- **Scalability:** The current implementation still processes PDFs page by page. While DBNet++ improves detection accuracy, the overall scalability for very large documents or batch processing remains a future consideration.

---

### Design Trade-offs

By explicitly separating the detection and recognition steps within `run_ocr`, we gain better control over the OCR pipeline and can leverage DBNet++'s specific capabilities. This adds a slight increase in code complexity compared to a single `ocr.ocr` call, but it aligns with the goal of integrating DBNet++ more deeply and provides a clearer path for future enhancements like custom pre/post-processing based on detection results.

---
Please review and approve the merge.
