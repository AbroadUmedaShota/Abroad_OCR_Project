このIssueでは、OCRの精度向上を目的として、複数のOCRエンジンの結果を統合するEnsemble Votingと、認識結果を言語モデルで補正するKenLM Correctionを実装します。

具体的には、以下の作業を行います。

*   `src/ocr_poc.py` にEnsemble Voting (Weighted Voting Fusion) のロジックを実装します。
*   `src/ocr_poc.py` にKenLM Correctionのロジックを実装します。
*   `scripts/` ディレクトリにKenLMモデルのロードと適用を行うための補助スクリプトを追加します（必要であれば）。
*   `tests/` ディレクトリにEnsemble VotingとKenLM Correctionのテストケースを追加します。
*   `SDD.md` の関連セクション（4.3 OCR エンジン Layer, 4.4 Pre/Post 処理, 5.2 Voting & スペース保持, 5.3 KenLM 補正）を更新します。
*   `docs/00_PROJECT_OVERVIEW.md` と `docs/01_ARCHITECTURE.md` を更新し、Ensemble VotingとKenLM Correctionの実装を反映させます。