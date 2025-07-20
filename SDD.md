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

```text
┌──────────┐   ┌────────────┐   ┌──────────────┐
│ UI / CLI   │→ │ PipelineMgr │→ │ PDF Builder  │→ Searchable PDF
└──────────┘   └────┬───────┘   └──────────────┘
                     ↓
           ┌─────────────────────────────┐
           │ OCR Engine Layer (Plugin)   │
           │  • Tesseract 5.4 (印字)      │
           │  • PP‑OCRv5 (印字+手書き)     │
           │  • Mistral‑OCR LoRA (手書き) │
           │  • Weighted Voting Fusion   │
           └─────────────────────────────┘
                     ↓
           ┌───────────────────────────┐
           │ Pre/Post‑Processing       │
           │  • OpenCV    (deskew etc) │
           │  • KenLM 5‑gram 修正       │
           └───────────────────────────┘
```

### 4.1 UI レイヤ

* **Tauri + React**: 軽量 (<15 MB) バイナリ化。
* ドラッグ&ドロップ投入、進捗/残時間表示。
* 低信頼テキストのインライン編集と即時再埋込。

### 4.2 Pipeline Manager

* ファイル監視→ジョブキュー実装 (Tokio)。
* JSON 定義されたパイプライン DAG を解決し並列実行。

### 4.3 OCR エンジン Layer

| エンジン                               | 用途       | 出力        | 備考                  |
| ---------------------------------- | -------- | --------- | ------------------- |
| Tesseract 5.4 (finetune `ja_vert`) | 印字横書/縦書  | 文字 + conf | OSS, Fast ICU 連携    |
| PP‑OCRv5                           | 印字+手書き混在 | 行矩形 + 文字  | PaddlePaddle C++ 推論 |
| Mistral‑OCR LoRA                   | 手書き特化    | 文字 + conf | 8‑bit 量子化, OpenVINO |

Voting: `score = conf × weight_engine` で最大値採択、空白は独立カウンタ。

#### 4.3.1 Mistral‑OCR LoRA のアーキテクチャ

* **種別**: Vision → Text の CNN‑Transformer ハイブリッド (Swin‑x Patch + causal decoder)
* **パイプライン位置**: DBNet++ が抽出した *行画像* に対し単体で文字認識
* **学習方針**: 8‑bit 量子化済み Mistral‑OCR (14B) を LoRA Rank‑32 でファインチューニング
* **入出力**: 入力 224×N PNG、出力 (UTF‑8 文字列, confidence float)
* **役割**: 手書き区間で Tesseract が低信頼なブロックの補完を担う

#### 4.3.2 異粒度出力の正規化 (文字 vs 行)

| ステップ          | 内容                                            |
| ------------- | --------------------------------------------- |
| 1. Glyph 切り出し | 行ベース出力を文字境界で分割し文字粒度へ                          |
| 2. 信頼度スケーリング  | 各エンジン conf を **Z‑score 正規化** (ページ単位) し共通スケール化 |
| 3. スペース挿入     | CTC blank → 空白トークンへマッピングし欠損補償                 |
| 4. Voting     | 正規化 `conf × weight` 比較で最終選択                   |

### 4.4 Pre/Post 処理

* **前処理**: bilateral→adaptive threshold→deskew→denoise。
* **後処理**: KenLM 5‑gram + domain 辞書。空白トークンを語彙化。

### 4.5 PDF Builder

* `pikepdf` で元 PDF を複製。
* 各行の bbox を PDF user‑space 座標に変換し Invisible‑Text レイヤ挿入。
* `confidence < 0.85` の行は赤ハイライト注釈を埋め込む。

---

## 5. アルゴリズム詳細

### 5.1 レイアウト検出 (DBNet++)

* 入力: 768×768 画像タイル、stride 32。
* 出力ポリゴンを最小外接矩形化→bbox。
* IoU < 0.8 行は再推論 (スケール+15 %)。

### 5.2 Voting & スペース保持

> **備考**: `preserve_spaces` は Voting 後段で実行し、最終採択テキストに空白トークン列を再挿入してエンジン間の空白欠損差を吸収する。

```pseudo
for line in detected_lines:
    results = []
    for engine in engines:
        text, conf = engine.recognize(line)
        results.append((text, conf * weight[engine]))
    best = max(results, key=lambda x: x[1])
    merged_text = preserve_spaces(best.text)
```

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

| テスト     | 方法                     | 合格基準    |
| ------- | ---------------------- | ------- |
| 印字 CER  | `scripts/calculate_cer.py` を使用 | ≤ 2 %   |
| 手書き CER | `scripts/calculate_cer.py` を使用  | ≤ 5 %   |
| IoU     | mean IoU 全行            | ≥ 0.80  |
| 空白整合    | 空白トークン CER             | ≤ 1 %   |
| 性能      | 50 p / CPU             | ≤ 5 min |
| メモリ     | Peak RSS               | ≤ 8 GB  |
| 長期試験    | 隔離LAN 72 h             | クラッシュ 0 |

自動評価スクリプトは `tests/` に配置し GitHub Actions で実行。

### 9.1. βテスト計画

- **目的**: 実際のユーザー環境での機能性、ユーザビリティ、安定性の検証。
- **対象**: 外部のテストユーザー（最大10名）。
- **期間**: 2週間。
- **フィードバック収集**: GitHub Issues (バグ報告、機能要望) および専用のフィードバックフォーム。
- **スコープ**: 全ての主要機能（PDF変換、OCR処理、CSV出力、IoUチェック）。

### 9.2. 負荷試験計画

- **目的**: 大量データ処理時のパフォーマンス、リソース消費、安定性の評価。
- **ツール**: Pythonの`multiprocessing`モジュールと`time`モジュールを用いたカスタムスクリプト。
- **シナリオ**: 100ページ以上のPDFファイルを連続して処理。
- **評価指標**: ページあたりの処理時間、CPU/メモリ使用率、エラー発生率。
- **合格基準**: 50ページ/CPUコアあたり5分以内、メモリ使用量8GB以下、エラー発生率0%。

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

| Sprint | 期間     | マイルストーン                        |
| ------ | ------ | ------------------------------ |
| 0      | W‑1    | リポジトリ/CI 雛形作成                  |
| 1      | W1‑2   | PDF → image → PP‑OCRv5 CLI PoC |
| 2      | W3‑4   | DBNet++ 統合 + CER 計測            |
| 3      | W5‑6   | Ensemble Voting + KenLM 補正     |
| 4      | W7‑8   | LoRA 微調整 + 精度レビュー              |
| 5      | W9‑10  | Tauri UI α版・IoU チェック実装         |
| 6      | W11‑12 | βテスト・負荷試験・リリース候補               |

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
