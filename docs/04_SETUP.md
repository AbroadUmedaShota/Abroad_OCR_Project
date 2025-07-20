# 04_SETUP.md

## 1. 開発環境のセットアップ

本プロジェクトをローカルで開発・実行するためのセットアップ手順を説明します。

### 1.1. 前提条件

- Python 3.8 以降
- Git

### 1.2. リポジトリのクローン

まず、プロジェクトのリポジトリをクローンします。

```bash
git clone https://github.com/AbroadUmedaShota/Abroad_OCR_Project.git
cd Abroad_OCR_Project
```

### 1.3. 依存関係のインストール

必要なPythonパッケージをインストールします。`requirements.txt`に記載されているパッケージがインストールされます。

```bash
pip install -r requirements.txt
```

### 1.4. PaddleOCRモデルのダウンロード

PaddleOCRは初回実行時にモデルを自動的にダウンロードしますが、事前に手動でダウンロードしておくことも可能です。`src/ocr_poc.py`が使用する日本語モデルは、`lang='japan'`で指定されています。

## 2. PoCの実行方法

実装されたProof of Concept (PoC) は、CLIツールとして提供されています。PDFファイルを指定してOCR処理を実行し、結果をCSVファイルとして出力します。

### 2.1. 基本的な実行コマンド

```bash
python src/ocr_poc.py [PDFファイルへのパス]
```

例:

```bash
python src/ocr_poc.py tests/test.pdf
```

このコマンドは、指定されたPDFファイルを処理し、PDFファイルと同じディレクトリに`[元のPDF名]_ocr_results.csv`という名前のCSVファイルを生成します。

### 2.2. オプション

- `--no-csv`: OCR結果をCSVファイルに出力しません。

例:

```bash
python src/ocr_poc.py tests/test.pdf --no-csv
```

## 3. テストの実行方法

開発中に変更を加えた場合は、以下のコマンドでユニットテストを実行し、機能が正しく動作することを確認してください。

```bash
python -m unittest tests/test_ocr_poc.py
```
