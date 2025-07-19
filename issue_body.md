<<<<<<< HEAD
このIssueでは、OCRの精度をさらに向上させるため、Mistral-OCR LoRAの微調整と、詳細な精度レビューを実施します。

具体的には、以下の作業を行います。

*   `SDD.md`の「6. モデル学習・更新」に記載されているLoRA微調整のフェーズ（LoRA初期、Phase-A、Phase-B）を実装します。
*   手書き文字認識に特化したMistral-OCR LoRAモデルの学習パイプラインを構築します。
*   CER計測機能を用いて、印字および手書き文字のOCR精度を詳細にレビューします。
*   `src/ocr_poc.py`または新しいモジュールに、LoRAモデルを利用するロジックを統合します。
*   `tests/`ディレクトリに精度レビュー用のテストデータとテストケースを追加します。
*   `SDD.md`の関連セクション（特に「4.3 OCR エンジン Layer」と「6. モデル学習・更新」）を更新します。
*   `docs/00_PROJECT_OVERVIEW.md`と`docs/01_ARCHITECTURE.md`を更新し、LoRA微調整と精度レビューの統合を反映させます。
=======
このIssueでは、OCRの精度をさらに向上させるため、複数のOCRエンジンの結果を統合するEnsemble Votingと、言語モデルを用いたKenLM補正を実装します。

具体的には、以下の作業を行います。

*   `SDD.md`の「4.3 OCR エンジン Layer」に記載されているEnsemble Votingのロジック（`score = conf × weight_engine` で最大値採択、空白は独立カウンタ）を実装します。
*   `SDD.md`の「5.3 KenLM 補正」に記載されているKenLM補正のロジックを実装します。
*   `src/ocr_poc.py`または新しいモジュールにこれらの機能を統合します。
*   `tests/`ディレクトリにEnsemble VotingとKenLM補正のテストケースを追加します。
*   `SDD.md`の関連セクション（特に「4.3 OCR エンジン Layer」と「5.3 KenLM 補正」）を更新します。
*   `docs/00_PROJECT_OVERVIEW.md`と`docs/01_ARCHITECTURE.md`を更新し、Ensemble VotingとKenLM補正の統合を反映させます。
>>>>>>> origin/main
