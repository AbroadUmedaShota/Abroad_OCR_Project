このIssueでは、OCRアプリケーションのTauri UIアルファ版を実装し、IoUチェック機能を統合します。

具体的には、以下の作業を行います。

*   Tauriプロジェクトを初期化し、基本的なUIフレームワークをセットアップします。
*   PDFの入力、OCR処理の開始、CSV出力のパス指定など、主要なCLI機能をUIから操作できるようにします。
*   `scripts/accuracy_reviewer.py` で実装されたIoUチェック機能をUIに統合し、OCR結果の視覚的なフィードバックを提供します。
*   `SDD.md` の関連セクション（4.1 UI レイヤ、3.6 IoU Check）を更新します。
*   `docs/00_PROJECT_OVERVIEW.md` と `docs/01_ARCHITECTURE.md` を更新し、Tauri UI と IoU チェックの実装を反映させます。
*   UI のテストケースを追加します。