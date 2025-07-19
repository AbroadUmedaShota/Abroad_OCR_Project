このIssueでは、OCRの精度向上と評価のためにDBNet++を統合し、Character Error Rate (CER) の計測機能を実装します。

具体的には、以下の作業を行います。

*   DBNet++をPaddleOCRパイプラインに統合し、より正確なテキスト領域検出を可能にします。
*   `src/ocr_poc.py`または新しいモジュールにCER計測機能を追加します。
*   `tests/`ディレクトリにCER計測用のテストデータとテストケースを追加します。
*   `SDD.md`の関連セクション（特に「3.2 品質要件」と「9. テスト計画」）を更新します。
*   `docs/00_PROJECT_OVERVIEW.md`と`docs/01_ARCHITECTURE.md`を更新し、DBNet++の統合を反映させます。