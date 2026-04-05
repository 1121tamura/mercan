# mercan プロジェクト仕様書

Claude Codeへの引き継ぎ用ドキュメント。
このドキュメントをClaude Codeにコピペして作業を開始してください。

---

## プロジェクト概要

メルカリの販売情報を取得し、確定申告資料データを作成するデスクトップアプリケーション。
本業での技術スタック検証（DDD + Clean Architecture）という裏テーマも兼ねる。

---

## スコープ

### フェーズ1（今回作る）
- メルカリ出品データ・売却済みデータ取得（Chrome拡張経由）
- 経費管理（仕入れ・送料・その他）
- 在庫（棚卸資産）管理
- 確定申告データ出力（freee / 弥生 CSV形式）

### フェーズ2（将来検討）
- ヤフオク・その他プラットフォームへの対応拡張
- 時間指定・条件指定の一斉値下げ機能

---

## 技術スタック

| レイヤー | 技術 |
|---|---|
| デスクトップ | Electron + electron-builder |
| 自動更新 | electron-updater（GitHub Releases経由） |
| フロントエンド | React + TypeScript + Vite |
| UIコンポーネント | shadcn/ui + Tailwind CSS |
| バックエンド | Python 3.12 + FastAPI |
| DB | SQLite + SQLAlchemy |
| マイグレーション | Alembic |
| パッケージ管理（Python） | uv |
| アーキテクチャ | DDD + Clean Architecture |
| テスト | pytest（backend） / Vitest（frontend） |
| CI/CD | GitHub Actions |
| 配布 | electron-builder（Win/Mac インストーラー） |

---

## 対応OS

- Windows
- Mac
（electron-builderで両対応）

---

## 開発環境

- VSCode Dev Container（Docker Desktop使用・Mac上で開発）
- ElectronのみホストMacで実行（コンテナ内ではGUI起動不可のため）

### 役割分担

| 実行場所 | 内容 |
|---|---|
| Dev Container内 | Python + FastAPI / React + Vite / Chrome拡張（TypeScript） |
| ホストMac | Electronアプリの起動・ビルドのみ |

### 開発時の起動イメージ

```
ターミナル1（Dev Container内）
$ uvicorn main:app --reload
→ localhost:8000 でFastAPI起動

ターミナル2（Dev Container内）
$ npm run dev
→ localhost:5173 でReact起動

ターミナル3（ホストMacで）
$ npm run electron:dev
→ ElectronがReact+FastAPIに接続して起動
```

---

## リポジトリ構成

```
mercan/
├── .devcontainer/
│   ├── devcontainer.json       # Python3.12 + Node.js + uv + VS Code拡張設定
│   └── docker-compose.yml      # 開発環境のみ（本番・配布には不要）
├── .github/
│   └── workflows/
│       ├── ci.yml              # pytest + ruff + vitest + eslint
│       └── release.yml         # Win/Macビルド → GitHub Releasesへ自動アップロード
├── electron/
│   ├── main.ts                 # Pythonプロセス起動・Windowの管理
│   └── preload.ts              # contextBridge（セキュアなIPC通信）
├── frontend/
│   └── src/
│       ├── pages/
│       ├── components/
│       ├── hooks/
│       └── lib/                # APIクライアント（localhost:8000へHTTP通信）
├── backend/
│   ├── presentation/           # FastAPIルーター・スキーマ
│   │   ├── routers/
│   │   └── schemas/
│   ├── application/            # ユースケース・DTO
│   │   ├── usecases/
│   │   └── dtos/
│   ├── domain/                 # ドメインモデル（ビジネスロジック）
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── repositories/       # インターフェース定義のみ
│   │   └── services/
│   ├── infrastructure/         # DBや外部連携の実装
│   │   ├── repositories/       # SQLite実装
│   │   ├── database/
│   │   └── parsers/            # メール・CSVパーサー
│   ├── tests/
│   ├── main.py
│   └── pyproject.toml          # uv管理
└── chrome-extension/           # データ取得用Chrome拡張（Manifest V3）
    ├── manifest.json
    ├── content.ts
    └── background.ts
```

---

## アーキテクチャ（DDD + Clean Architecture）

### ドメイン設計

```
domain/
├── entities/
│   ├── SalesRecord        # 売却済み販売記録（集約ルート）
│   ├── InventoryItem      # 在庫（出品中商品）
│   ├── Expense            # 経費
│   └── TaxReport          # 確定申告レポート
├── value_objects/
│   ├── Money              # 金額（円）
│   ├── SaleDate           # 売却日
│   ├── FiscalYear         # 会計年度
│   ├── ItemName           # 商品名
│   └── Platform           # プラットフォーム識別子（MERCARI / YAHOO_AUCTION / ...）
└── repositories/          # インターフェースのみ（実装はinfrastructure層）
    ├── ISalesRecordRepository
    ├── IInventoryItemRepository
    ├── IExpenseRepository
    └── ITaxReportRepository
```

### マルチプラットフォーム対応設計方針

取得元を増やせるよう、Infrastructure層にプロバイダー抽象化を設ける。

```
infrastructure/
└── providers/
    ├── IMarketplaceProvider    # 取得インターフェース（domain層に定義）
    ├── MercariProvider         # メルカリ実装
    └── YahooAuctionProvider    # ヤフオク実装（フェーズ2）
```

**IMarketplaceProvider が持つ責務：**
- 売却済みデータの取得（差分・全件）
- 出品中データの取得

**Platformの役割：**
- どのプラットフォーム由来のデータかをエンティティに保持する
- 手数料率など、プラットフォームごとの差異はProviderが吸収する
  - メルカリ：販売価格の10%
  - ヤフオク：落札システム利用料（8.8% + 振込手数料 等）

### レイヤー構成

```
Presentation Layer  → FastAPIルーター・リクエスト/レスポンススキーマ
Application Layer   → ユースケース・DTO
Domain Layer        → エンティティ・値オブジェクト・リポジトリIF・ドメインサービス
Infrastructure Layer→ SQLite実装・外部サービス連携
```

### FastAPIのルーティング設計方針

`main.py` はFastAPIのルール上の入り口ではなく、uvicornの起動コマンドで指定するモジュール名が入り口になる慣習。

```bash
uvicorn main:app  # main.py の app を起動（慣習）
```

DRFとの対比：

| DRF | FastAPI |
|---|---|
| `wsgi.py`（アプリ初期化） | `main.py`（アプリ初期化） |
| ルートの `urls.py`（ルーター登録） | `main.py`（`include_router` 登録） |
| アプリごとの `urls.py` | `presentation/routers/` 配下の各ファイル |

- `main.py` = DRFの `wsgi.py` + ルートの `urls.py` を1ファイルに合体させたもの
- 機能ごとに `APIRouter` を作成し `main.py` で `include_router()` して登録する

---

## データモデル（主要エンティティ）

### SalesRecord（売却済み販売記録）
```
- id
- platform          # プラットフォーム（MERCARI / YAHOO_AUCTION / ...）
- platform_item_id  # 各プラットフォーム側のID（重複防止のキー）
- item_name         # 商品名
- sold_price        # 販売価格
- fee               # 手数料（プラットフォームごとに計算）
- profit            # 販売利益
- sold_at           # 売却日（確定申告の基準日）
- fetched_at        # 取得日時（差分管理用）
```

### InventoryItem（在庫）
```
- id
- platform          # プラットフォーム（MERCARI / YAHOO_AUCTION / ...）
- platform_item_id  # 各プラットフォーム側のID
- item_name
- purchase_price    # 仕入れ価格
- listed_at         # 出品日
- status            # 出品中 / 売却済み
```

### Expense（経費）
```
- id
- category          # 仕入れ / 送料・梱包材 / その他
- amount            # 金額
- description       # 内容メモ
- occurred_at       # 発生日
- related_item_id   # 関連商品ID（任意）
```

### SyncHistory（同期履歴）
```
- id
- synced_at         # 最終同期日時
- total_count       # 取得件数
- status            # 成功 / 失敗
```

---

## 利益計算ロジック

```
年間利益 =
  売上合計（売却済み）
  - メルカリ手数料合計
  - 経費合計（仕入れ・送料・その他）
  - 期首在庫金額
  + 期末在庫金額（棚卸資産）
```

---

## データ取得方式

### 採用方式：Chrome拡張 × 内部APIアクセス

各プラットフォームに公式CSV出力機能がないため、
自前のChrome拡張機能（Chrome Web Store配布）を使いデータを取得する。

#### 取得フロー（共通）

```
① ユーザーが対象プラットフォームにログイン済みの状態で拡張のボタンを押す
② 拡張が内部APIに100件ずつリクエスト（1〜2秒インターバル）
③ 全件まとめてJSONファイルをローカルに保存（platformフィールド付き）
④ ElectronアプリがJSONを読み込みSQLiteに保存
```

#### プラットフォーム別の対応状況

| プラットフォーム | フェーズ | 手数料率 |
|---|---|---|
| メルカリ | フェーズ1 | 販売価格の10% |
| ヤフオク | フェーズ2 | 落札システム利用料8.8% 等 |

#### 初回 vs 差分取得

| | 内容 | 時間目安 |
|---|---|---|
| 初回 | 全件取得（数万件） | 約5〜10分 |
| 月次 | 前回同期日以降に売却されたもののみ | 数十秒 |

#### 重複防止
- `mercari_item_id`をキーとして重複チェック
- 同じIDが既にDBに存在する場合はスキップ

#### リスク
- 利用規約上グレーゾーン（自己責任・配布時に明記）
- メルカリのAPI仕様変更で壊れる可能性あり（自前のため即修正可能）
- リクエスト間隔1〜2秒でレート制限リスクを最小化

---

## 確定申告データ出力

- **freee**：freee公式CSVインポート仕様に準拠したCSVを生成
- **弥生**：弥生会計の仕訳日記帳インポート形式CSVを生成
- APIキー不要。ユーザーが各サービスに手動インポートする方式。

---

## アプリ自動更新

- `electron-updater` を使用
- GitHub Releasesをサーバーとして使用（費用ゼロ）
- タグをpushするだけでGitHub Actionsが自動ビルド・リリース
- ユーザーはアプリ起動時に自動で新バージョンを検知・更新

---

## GitHub Actions構成

### ci.yml（PRのたびに実行）
- Python：pytest + ruff + mypy
- Frontend：vitest + eslint + tsc

### release.yml（tagプッシュ時に実行）
- Windows：exeインストーラー生成
- Mac：dmgインストーラー生成
- GitHub Releasesに自動アップロード

---

## 作業ステップ

以下の順番で実装を進める。

```
Step 1. リポジトリ・全体構成の雛形
  - .devcontainer/ 作成（devcontainer.json + docker-compose.yml）
  - .github/workflows/ 作成（ci.yml + release.yml 雛形）
  - ディレクトリ構成作成
  - .gitignore（Python/Node/Electron対応）
  - README.md

Step 2. バックエンド（Python + FastAPI）セットアップ
  - uv init
  - FastAPI + SQLAlchemy + Alembic インストール
  - DDD構成のディレクトリ・雛形ファイル作成
  - ヘルスチェックAPI（GET /health）実装

Step 3. フロントエンド（React + TypeScript + Vite）セットアップ
  - Vite + React + TypeScript 初期化
  - shadcn/ui + Tailwind CSS セットアップ
  - バックエンドへのAPIクライアント雛形

Step 4. Electronセットアップ
  - electron + electron-builder セットアップ
  - Pythonプロセス起動・終了処理
  - electron-updater セットアップ
  - フロントエンドの表示

Step 5. Chrome拡張セットアップ
  - manifest.json（Manifest V3）
  - メルカリAPIアクセスの雛形
  - ElectronアプリへのJSON受け渡し

Step 6. GitHub Actions 完成
  - ci.yml（pytest + ruff + vitest + eslint）
  - release.yml（Win/Macビルド）
```

---

## 補足・注意事項

- Dev Containerはあくまで開発環境定義。本番・配布には不要。
- 配布時はPythonをPyInstallerでexe/appに同梱。ユーザーはDockerもPythonもインストール不要。
- Chrome拡張はChrome Web Storeから配布。メルカリUI変更で壊れた際は迅速に修正・更新する。
- 本業での検証目的のため、DB以外の技術スタックは本業環境と揃えた設計にする。
