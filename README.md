# オフライン日本語手書き対応・検索可能 PDF 生成アプリ

このプロジェクトは、機微情報を含むPDF文書を完全オフライン環境でOCR処理し、検索可能なPDFへ変換するアプリケーションです。

## 特徴

- **完全オフライン動作**: ネットワーク接続なしでOCR処理を実行。
- **高精度OCR**: 日本語の手書き文字および印字文字に対応。
- **検索可能PDF生成**: OCR結果を埋め込んだ検索可能なPDFを出力。
- **CSV出力**: OCR結果をCSVフォーマットでも出力。

## セットアップ

このプロジェクトをローカルでセットアップするには、以下の手順に従ってください。

1.  リポジトリをクローンします。
    ```bash
    git clone https://github.com/AbroadUmedaShota/Abroad_OCR_Project.git
    ```
2.  プロジェクトディレクトリに移動します。
    ```bash
    cd Abroad_OCR_Project
    ```
3.  依存関係をインストールします。
    ```bash
    pip install -r requirements.txt
    ```

**CI/CD:**

GitHub Actionsが設定されており、`main`ブランチへのプッシュまたはプルリクエスト時に自動的にビルド、テスト、リントが実行されます。

## 使い方

PDFファイルに対してOCRを実行するには、以下のコマンドを使用します。

```bash
python src/ocr_poc.py <PDFファイルのパス>
```

例:
```bash
python src/ocr_poc.py tests/test.pdf
```

OCR結果は、入力PDFファイルと同じディレクトリに`<PDFファイル名>_ocr_results.csv`として出力されます。

### オプション

*   `--no-csv`: OCR結果をCSVファイルに出力しません。
*   `--zip`: PDFファイルとOCR結果のCSVファイルをZIPアーカイブにまとめます。

例:
```bash
python src/ocr_poc.py tests/test.pdf --zip
```

## 開発

(準備中)

## ライセンス

(準備中)
