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

### 3.2. OCR パイプライン (PoC)

PoC では CLI 内にシンプルな直列パイプラインを実装し、以下のモジュールで構成します。

1. **PdfPageExtractor** (`pdf_to_images`) – PyMuPDF を利用して PDF をページ画像へ変換。
2. **PaddleOCREngine** – PaddleOCR を叩いて行レベル結果を取得。
3. **WeightedVotingAggregator (計画)** – 複数エンジンの結果をアライン・集約。
4. **PostProcessorPipeline** – `_remove_redundant_cjk_spaces` と KenLM 補正を順番に適用。
5. **CsvExporter** – 正規化済みデータを CSV に書き出し。

これらのモジュールを関数ベースで実装し、将来はクラス化して GUI からも再利用できる構造とする。

### 3.3. Engine Adapter

複数エンジンの導入を容易にするため、エンジンごとの差異を吸収する `EngineAdapter` プロトコルを新設する。既存の PaddleOCR 呼び出しは `PaddleOCREngine` として抽象化し、Tesseract や手書き特化モデルを同じインターフェースで接続できるようにする。

### 3.4. Result Aggregation & Post Processing

- **Weighted Voting Fusion**: 行アライメント、スコア正規化、重み付き最大選択、候補保持までを担う独立クラス。
- **KenLM Corrector**: `scripts/kenlm_corrector.py` でラップされた KenLM API を呼び出し、n-best 候補をスコアリングする。
- **スペース正規化**: `_remove_redundant_cjk_spaces` を再利用し、CJK 間スペースを最終段で調整。

### 3.5. PDF Builder (将来)

検索可能 PDF 生成は PoC 後に `PdfOverlayWriter` として追加し、CSV と同じ構造体を入力に不可視テキストレイヤを構成する。

### 3.6. パフォーマンス/品質計測

`tests/test_ocr_poc.py` に Weighted Voting のユニットテスト、`scripts/calculate_cer.py` で CER 計測を実施する。行検出 IoU は今後追加予定の評価スクリプトで担保する。

## 4. データフロー (PoC)

現在の PoC におけるデータフローは以下の通りです。

1. **PDF 入力**: CLI で PDF ファイルを指定。
2. **画像変換**: `pdf_to_images` がページ画像を生成。
3. **OCR 処理**: `run_ocr` が PaddleOCR を呼び出し、行単位の認識結果を得る。
4. **結果集約**: 1 エンジン構成のためダイレクトに配列へ格納。将来は Weighted Voting を経由。
5. **CSV 出力**: 結果を `page`, `block_id`, `x0`, `y0`, `x1`, `y1`, `text`, `confidence` で保存。

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