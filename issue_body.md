このIssueでは、OCRの精度をさらに向上させるため、複数のOCRエンジンの結果を統合するEnsemble Votingと、言語モデルを用いたKenLM補正を実装します。

具体的には、以下の作業を行います。

*   `SDD.md`の「4.3 OCR エンジン Layer」に記載されているEnsemble Votingのロジック（`score = conf × weight_engine` で最大値採択、空白は独立カウンタ）を実装します。
*   `SDD.md`の「5.3 KenLM 補正」に記載されているKenLM補正のロジックを実装します。
*   `src/ocr_poc.py`または新しいモジュールにこれらの機能を統合します。
*   `tests/`ディレクトリにEnsemble VotingとKenLM補正のテストケースを追加します。
*   `SDD.md`の関連セクション（特に「4.3 OCR エンジン Layer」と「5.3 KenLM 補正」）を更新します。
*   `docs/00_PROJECT_OVERVIEW.md`と`docs/01_ARCHITECTURE.md`を更新し、Ensemble VotingとKenLM補正の統合を反映させます。