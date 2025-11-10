# オフライン日本語手書き対応・検索可能 PDF 生成アプリ設計書

## 1. 目的と背景

機微情報を含む PDF 文書を **完全オフライン環境** で OCR 処理し、検索可能 PDF へ変換する。特に日本語の手書き文字を含む混在文書で **印字 CER ≥ 98 %**、**手書き CER ≥ 95 %**、**バウンディング IoU ≥ 0.80**、**スペース厳守** を達成することを目的とする。

---

## 2. 用語集

| 用語                   | 定義                                             |
| -------------------- | ---------------------------------------------- |
| CER                  | Character Error Rate = (置換+挿入+削除) / 総文字数       |
| IoU                  | Intersection over Union。検出バウンディングボックスが GT を覆う率 |
| 空白トークン               | 半角/全角スペースそれぞれを保持する特殊トークン                       |
| Invisible‑Text Layer | PDF 内テキスト抽出用の不可視テキストレイヤ                        |

---

## 3. 機能要件

### 3.1 OCR 対象

* PDF 全ページ (画像 PDF・混在 PDF)。
* 文字種: 漢字、ひらがな、カタカナ、英字、アラビア数字、記号。
* 印字および手書き文字双方を認識。

### 3.2 品質要件

| 指標           | 印字    | 手書き        |
| ------------ | ----- | ---------- |
| OCR 精度 (CER) | ≤ 2 % | ≤ 5 %      |
| バウンディング IoU  | -     | ≥ 0.80     |
| 空白保持         | -     | エラー率 ≤ 1 % |

### 3.3 非機能要件\$1

### 3.4 出力形式

* OCR 結果を **指定 CSV フォーマット** でも出力し、検索可能 PDF と同じディレクトリへ保存する。
* **CSV カラム定義**: `page`, `block_id`, `x0`, `y0`, `x1`, `y1`, `text`, `confidence` の 8 列（UTF‑8, RFC 4180 準拠）。
* GUI／CLI の両方で *PDF + CSV* 同時出力をデフォルト動作とする（`--no-csv` で無効化可能）。
* オプション `--zip` により PDF と CSV を 1つの ZIP ファイルにまとめる。

---

## 4. システム全体構成

### 4.1 現行 PoC のデータフロー

```text
┌────────┐   ┌────────────┐   ┌─────────────┐
│   CLI    │ → │ PDF→Image  │ → │   OCR Core   │
└────────┘   └────────────┘   └──────┬──────┘
                                      │
                         ┌────────────┴────────────┐
                         │ Result Aggregator (WVF) │
                         └────────────┬────────────┘
                                      │
                         ┌────────────┴────────────┐
                         │ KenLM Corrector (予定)  │
                         └────────────┬────────────┘
                                      │
                         ┌────────────┴────────────┐
                         │ CSV / PDF Exporter (将来)│
                         └──────────────────────────┘
```

PoC 段階では CLI から `src/ocr_poc.py` を実行し、PyMuPDF によるページ画像化と PaddleOCR を用いた 1 エンジン構成で OCR を実施する。結果を CSV へ保存するところまでを自動化する。今後の開発で Weighted Voting Fusion (WVF) と KenLM 補正が順次組み込まれる前提で、コンポーネント境界を明確化した。

### 4.2 コンポーネントの責務

| コンポーネント | 役割 | 主な入出力 | 実装位置 |
| --- | --- | --- | --- |
| CLI (PoC) | PDF パス・オプション受け取り、処理開始 | 引数, ログ | `src/ocr_poc.py:main` |
| PDF→Image 変換 | PDF ページを PNG に変換 | PDF パス → 画像パス群 | `pdf_to_images` |
| OCR コア | 画像ごとに OCR 実行し行単位の結果を返却 | 画像パス → `List[LineResult]` | `run_ocr` 内エンジン呼び出し |
| Result Aggregator | 複数エンジン結果を整列・重み付け投票 | `List[EngineResult]` → `List[LineResult]` | `WeightedVotingAggregator` (新規) |
| KenLM Corrector | 言語モデルによる後処理 | 生テキスト → 補正テキスト | `scripts/kenlm_corrector.py` |
| Exporter | CSV と検索可能 PDF 出力 | 正規化結果 → ファイル | CSV: `run_ocr`、PDF: 将来 `PDFExporter` |

### 4.3 今後導入するモジュールのインターフェース

1. **EngineAdapter Protocol**: PaddleOCR や Tesseract 等を同一インターフェースで扱うための抽象化。
   ```python
   class EngineAdapter(Protocol):
       name: str
       weight: float

       def infer(self, image_path: Path) -> List[LineResult]:
           ...
   ```
   既存の PaddleOCR 呼び出しは `PaddleOCREngine` として切り出す。将来追加のエンジンは同じプロトコルを実装するだけでよい。

2. **WeightedVotingAggregator**: エンジンの結果を揃え、重み付き最大値を採択する責務を持つ純粋 Python クラス。スペース挿入や bbox 合成ロジックを統合する。

3. **PostProcessorPipeline**: KenLM 補正や空白整理などを連結する軽量パイプライン。PoC では `_remove_redundant_cjk_spaces` のみ、KenLM 導入後は `KenLMCorrector.correct()` をチェーンする。

### 4.4 GUI / Pipeline Manager の位置付け

GUI (Tauri + React) や監視ベースの Pipeline Manager はフェーズ 2 以降に追加する。PoC の CLI で動作するモジュールを独立させることで、GUI 化時には UI から CLI と同一 API を呼び出すだけで済む。

### 4.5 PDF Builder (将来)

検索可能 PDF 生成は次フェーズで `PdfOverlayWriter` クラスとして実装し、CSV 生成と同じ構造化データを入力として扱う。Invisible-Text レイヤと低信頼ハイライト挿入要件は維持する。

---

## 5. アルゴリズム詳細

### 5.1 レイアウト検出

PP‑OCRv5 が同梱する DB++ 検出器を使用し、行レベルのクアドラティック bbox を取得する。`run_ocr` では PaddleOCR の戻り値（4 点ポリゴン + テキスト + 信頼度）を標準化して扱う。将来的に別エンジンを加える際は、Adapter 層で以下の構造体に変換する。

```python
LineResult = TypedDict(
    "LineResult",
    {
        "bbox": Tuple[Point, Point, Point, Point],
        "text": str,
        "confidence": float,
    },
)
```

### 5.2 Weighted Voting Fusion とスペース保持

1. **行アライメント**: ページ単位で各エンジンの行数を比較し、bbox の IoU が 0.7 以上のものを同一行と見なす。ポリゴン数が一致しない場合は x 座標で近傍探索を行う。
2. **スコア正規化**: `score = sigmoid((conf - μ_engine) / σ_engine)` でエンジンごとの信頼度を正規化し、重み付きスコア `score × weight_engine` を算出する。μ, σ はページ内の信頼度分布から算出する。
3. **投票**: 各行に対し最も高スコアのテキストを採択し、低位候補は `alternatives` 配列として保持する（KenLM 用）。
4. **スペース整理**: `_remove_redundant_cjk_spaces` を適用し、CJK 連続区間に挿入された不要スペースを除去する。同時に、エンジン間で空白が欠落している場合は補完する。

### 5.3 KenLM 補正

```
# KenLM 補正: 認識結果を言語モデルで補正
# 候補となるテキスト列 (n-best list) を生成し、KenLM モデルでスコア付け
# 最もスコアの高い候補を最終結果として採用
score = log P(sentence|LM)
Δ = score_best - score_alt  # 対数確率差
if Δ > τ: choose best else alt
```

τ は Dev セットで最適化。

---

## 6. モデル学習・更新

LoRA微調整と精度レビューのプロセスを以下に詳述する。

### 6.1 LoRA微調整パイプライン

1.  **データ準備**: 手書き文字データセット（Kuzushiji-MNIST、社内帳票など）を収集・アノテーションし、モデル入力形式に変換する。
2.  **ベースモデル選択**: Mistral-OCR (14B) のような大規模な事前学習済みVision-Textモデルを選択する。
3.  **LoRAアダプターの初期化**: LoRA (Low-Rank Adaptation) 技術を用いて、ベースモデルの特定層（例: `q_proj`, `v_proj`）に低ランクアダプターをアタッチする。ランクは32に設定する。
4.  **ファインチューニング**: 準備したデータセットでLoRAアダプターのみを学習させる。これにより、少量のデータで効率的にモデルを特定のタスク（手書きOCR）に適合させることができる。
5.  **モデル保存**: ファインチューニング後、LoRAアダプターの重みのみを保存する。これにより、モデル全体の保存と比較してストレージ要件を大幅に削減できる。

### 6.2 精度レビュープロセス

1.  **OCR実行**: ファインチューニングされたLoRAモデルを含むOCRパイプラインで、テストデータセットに対してOCRを実行する。
2.  **結果収集**: OCR結果（テキスト、バウンディングボックス、信頼度）を構造化された形式（例: CSV、JSON）で収集する。
3.  **CER/IoU計算**: Ground Truthデータと比較し、`scripts/calculate_cer.py` および `scripts/calculate_iou.py` を用いて文字認識精度（CER）とバウンディングボックス精度（IoU）を計算する。
4.  **レポート生成**: 計算された精度指標と詳細な結果を含むレポートを生成する。これにより、モデルのパフォーマンスを評価し、改善点を特定できる。

| フェーズ    | データ                       | 目的     | 目標 CER      |
| ------- | ------------------------- | ------ | ----------- |
| LoRA 初期 | Kuzushiji‑MNIST + 5k 社内帳票 | 手書き特化  | 94 %        |
| Phase‑A | 10k 手書き行 + 別添2            | CER 改善 | 95 %        |
| Phase‑B | 20k + data aug            | 最終到達   | 96 % (バッファ) |

DBNet++ は別添 polygon ラベルで IoU 0.85 学習、mAP 0.92 想定。


---

## 7. システム要件

| 項目   | Minimum  | Recommended                 |
| ---- | -------- | --------------------------- |
| CPU  | 4‑core   | 8‑core+ AVX2                |
| GPU  | Optional | NVIDIA RTX 3060 / Intel Arc |
| RAM  | 8 GB     | 16 GB                       |
| Disk | 1 GB     | 3 GB (学習 checkpt)           |

---

## 8. セキュリティ / オフライン保証

1. 依存ライブラリとモデルを `resources/` に vendoring。
2. CI ビルド時に `--network none` で外部通信検知 → fail。
3. Runtime で `--offline` フラグを固定。外部ソケット生成禁止。

---

## 9. テスト計画

| テスト               | 方法                                           | 合格基準            |
| ------------------ | -------------------------------------------- | ----------------- |
| 印字 CER            | `scripts/calculate_cer.py` を使用                    | ≤ 2 %            |
| 手書き CER           | `scripts/calculate_cer.py` を使用                    | ≤ 5 %            |
| 行検出 IoU          | PaddleOCR 出力と GT の mean IoU                    | ≥ 0.80          |
| Weighted Voting 単体 | モックエンジン結果でユニットテスト (`tests/test_ocr_poc.py`) | 想定テキストへ一致 |
| KenLM 補正           | Dev セットで before/after CER を比較                 | CER 改善 ≥ 0.3 pt |
| 空白整合             | 空白トークン CER                                   | ≤ 1 %            |
| 性能                 | 50 p / CPU                                       | ≤ 5 min         |
| メモリ               | Peak RSS                                         | ≤ 8 GB          |
| 長期試験             | 隔離LAN 72 h                                      | クラッシュ 0       |

自動評価スクリプトは `tests/` に配置し GitHub Actions で実行。

### 9.1. βテスト計画

- **目的**: 実際のユーザー環境での機能性、ユーザビリティ、安定性の検証。
- **対象**: 外部のテストユーザー（最大10名）。
- **期間**: 2週間。
- **フィードバック収集**: GitHub Issues (バグ報告、機能要望) および専用のフィードバックフォーム。
- **スコープ**: 全ての主要機能（PDF変換、OCR処理、CSV出力、IoUチェック）。

### 9.2. 負荷試験計画

- **目的**: 大量データ処理時のパフォーマンス、リソース消費、安定性の評価。
- **ツール**: Python の `multiprocessing` + CLI を組み合わせたバッチスクリプト。
- **シナリオ**: 100 ページ以上の PDF を連続処理し、投票・KenLM が有効な状態で計測。
- **評価指標**: ページあたりの処理時間、CPU/メモリ使用率、失敗ジョブ数。
- **合格基準**: 50 ページ/CPU コアあたり 5 分以内、メモリ使用量 8 GB 以下、失敗ジョブ 0。

---

## 10. CI/CD & デプロイ

* GitHub Actions: Win/macOS/Linux クロスビルド。
* タグ push → `.dmg`, `.msi`, `.deb` を Release。
* Dockerfile (GPU) は CUDA 12 & PaddlePaddle 2.6 基盤。

### 10.1. リリース候補版の準備

- **ビルド**: GitHub Actionsを用いて、各OS向けの実行可能ファイルをビルドします。
- **バージョン管理**: セマンティックバージョニング（例: `v0.1.0-rc.1`）に従い、リリース候補版のタグを付与します。
- **配布**: GitHub Releasesを通じて、テストユーザー向けに配布します。
- **ドキュメント**: リリースノートとインストールガイドを更新します。

---

## 11. 開発ロードマップ

| Sprint | 期間     | マイルストーン                                           |
| ------ | ------ | ------------------------------------------------- |
| 0      | W‑1    | リポジトリ/CI 雛形作成、基本的な lint / test 導入                 |
| 1      | W1‑2   | PDF → Image → PaddleOCR CLI PoC、CSV 出力整備            |
| 2      | W3‑4   | EngineAdapter & WeightedVotingAggregator 実装、単体テスト追加 |
| 3      | W5‑6   | KenLM 補正パイプライン導入、n-best 生成 & 評価                  |
| 4      | W7‑8   | PDF Overlay Writer プロトタイプ、検索可能 PDF β版              |
| 5      | W9‑10  | Tauri UI α版、ジョブ管理 / 進捗表示                               |
| 6      | W11‑12 | 量産データでの検証、負荷試験・リリース候補                          |

---

## 12. リスク & 対策

| リスク          | 影響      | 対策                                                                               |
| ------------ | ------- | -------------------------------------------------------------------------------- |
| 手書き CER 未達   | 品質劣化    | 追加データ収集・LoRA epoch 延長・**多様筆跡 Data Augmentation (輝度/コントラスト変更, Elastic 変形, 微小回転)** |
| GPU 非搭載端末    | 性能低下    | OpenVINO + マルチスレッド最適化・**CPU 推論ベンチ (1 p/s) を Sprint‑1 で実測し Minimum 要件を検証**        |
| オフライン制限で依存欠落 | ビルド失敗   | 事前 vendoring & CI で通信検証                                                          |
| UI 校正 UX 複雑化 | ユーザ拒否反応 | 編集ガイド&ショートカット整備                                                                  |

---

## 13. 参照

* PP‑OCRv5 公式論文
* DBNet++: Progressive Differentiable Binarization
* KenLM Toolkit
* pikepdf Documentation

---

## 14. 将来拡張 (Table Recognition 等)

1. **テーブル構造認識**: PaddleOCR Table Recognition を統合し、CSV に `row_id`, `col_id` を追加して二次元関係を保持
2. **ZIP アーカイブ改善**: 複数文書バッチ処理時に `doc‑name/` サブフォルダ構造で圧縮
3. **Self‑Distillation**: LoRA 重みを Knowledge Distillation し CPU 向け軽量モデルを別途提供

*Prepared for engineering team — July 14 2025*
