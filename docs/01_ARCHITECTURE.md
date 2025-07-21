# 01_ARCHITECTURE.md

## 1. システム概要

本ドキュメントは、オフライン日本語手書き対応・検索可能PDF生成アプリケーションのアーキテクチャと設計思想を記述します。

## 2. 設計原則

- **オフラインファースト**: 全ての機能はネットワーク接続なしで動作するように設計されます。
- **モジュール性**: 各コンポーネントは独立性を保ち、容易に交換・拡張できるように設計されます。
- **高精度**: OCRエンジンおよび前処理・後処理において、高い認識精度とバウンディングボックスの正確性を追求します。
- **パフォーマンス**: 大量の文書処理にも耐えうるパフォーマンスを確保します。

## 3. 主要コンポーネント

### 3.1. UI/CLIレイヤ

ユーザーとのインタラクションを担当します。

- **CLI**: コマンドラインからの操作インターフェースを提供します。
- **GUI (将来)**: Tauri + Reactを用いたデスクトップアプリケーションとして、直感的な操作インターフェースを提供します。

### 3.2. Pipeline Manager (将来)

OCR処理のワークフローを管理します。

- ファイル監視、ジョブキューの実装。
- JSON定義されたパイプラインDAGを解決し、並列実行を管理します。

### 3.3. OCR Engine Layer

文字認識の中核を担います。複数のOCRエンジンをプラグインとして統合し、最適な結果を得るためのメカニズムを提供します。

- **PP-OCRv5**: 印字および手書き文字に対応した汎用OCRエンジン。DBNet++による高精度なテキスト領域検出が統合されています。
- **Tesseract 5.4 (将来)**: 印字に特化したOCRエンジン。
<<<<<<< HEAD
- **PaddleOCR with LoRA Fine-tuning (Implemented)**: The base PP-OCRv5 model can be fine-tuned using Low-Rank Adaptation (LoRA) to improve accuracy on specific datasets, particularly for handwritten characters.
=======
- **Mistral-OCR LoRA (将来)**: 手書き文字に特化したOCRエンジン。
>>>>>>> origin/main
- **Weighted Voting Fusion (枠組み導入済み)**: 複数のOCRエンジンの結果を統合し、最終的な認識結果を決定します。

### 3.4. Pre/Post-Processing

OCR処理の前後に画像処理や自然言語処理を行います。

- **前処理**: 画像の品質向上（例: deskew, denoise）。
- **後処理**: 認識結果の補正（例: KenLMを用いた言語モデル補正）。KenLM補正の枠組みが導入されています。

### 3.5. PDF Builder (将来)

OCR結果を元に検索可能なPDFを生成します。

- 元のPDFを複製し、不可視テキストレイヤーを挿入します。

### 3.6. IoU Check (枠組み導入済み)

OCR結果のバウンディングボックスの精度を評価します。

### 3.7. Fine-tuning and Evaluation

- **LoRA Fine-tuning**: A dedicated script (`scripts/fine_tune_lora.py`) allows for parameter-efficient fine-tuning of the PaddleOCR model on custom datasets.
- **Accuracy Evaluation**: A script (`scripts/evaluate_accuracy.py`) provides tools to measure the model's performance using Character Error Rate (CER) and Intersection over Union (IoU), ensuring a quantitative approach to accuracy improvements.

現在のPoCにおけるデータフローは以下の通りです。

1. **PDF入力**: ユーザーがCLIを通じてPDFファイルを指定します。
2. **画像変換**: PDFファイルがページごとに画像ファイルに変換されます。
3. **OCR処理**: 変換された画像に対してPP-OCRv5が実行され、テキストとバウンディングボックス情報が抽出されます。
4. **CSV出力**: 抽出されたOCR結果がCSV形式で出力されます。

## 5. 技術スタック

- **Python**: 主要な開発言語。
- **PyMuPDF (fitz)**: PDFの読み込みと画像変換に使用。
- **PaddleOCR**: OCRエンジンとして使用。
- **Tauri + React (将来)**: GUI開発フレームワーク。

## 6. 今後の展望

- 検索可能PDF生成機能の実装。
- GUIの開発。
- 複数のOCRエンジンの統合と結果の統合（Voting）。
- 高度な前処理・後処理機能の追加。
- モデル学習・更新パイプラインの構築。

## 7. 品質保証とリリース管理

- **βテスト**: 実際のユーザー環境での機能性、ユーザビリティ、安定性の検証。
- **負荷試験**: 大量データ処理時のパフォーマンス、リソース消費、安定性の評価。
- **リリース候補版の準備**: ビルド、バージョン管理、配布プロセスの確立。
