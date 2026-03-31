# mercan

メルカリの販売情報から確定申告資料を自動作成するデスクトップアプリ。

## 概要

mercan は、メルカリの販売履歴データを取り込み、確定申告に必要な収支計算・帳票出力を行うデスクトップアプリケーションです。Chrome拡張でメルカリの販売データを取得し、Electron製のデスクトップアプリで管理・出力します。

## 機能（フェーズ1）

- メルカリ出品データ・売却済みデータ取得（Chrome拡張経由）
- 経費管理（仕入れ・送料・その他）
- 在庫（棚卸資産）管理
- 確定申告データ出力（freee / 弥生 CSV形式）

## 技術スタック

| レイヤー | 技術 |
|---|---|
| デスクトップ | Electron + electron-builder |
| 自動更新 | electron-updater |
| フロントエンド | React + TypeScript + Vite |
| UIコンポーネント | shadcn/ui + Tailwind CSS |
| バックエンド | Python 3.12 + FastAPI |
| DB | SQLite + SQLAlchemy |
| マイグレーション | Alembic |
| パッケージ管理（Python） | uv |
| テスト | pytest / Vitest |
| Chrome拡張 | Manifest V3 |

## ディレクトリ構成

```
mercan/
├── backend/                  # Python FastAPI バックエンド
│   ├── presentation/         # ルーター・スキーマ
│   ├── application/          # ユースケース・DTO
│   ├── domain/               # エンティティ・値オブジェクト・リポジトリ
│   ├── infrastructure/       # DB・パーサー実装
│   ├── tests/
│   └── main.py
├── frontend/                 # React + TypeScript フロントエンド
│   └── src/
│       ├── pages/
│       ├── components/
│       ├── hooks/
│       └── lib/
├── electron/                 # Electron メインプロセス
│   ├── main.ts
│   └── preload.ts
├── chrome-extension/         # Chrome拡張（データ取得）
│   └── manifest.json
├── docs/
├── .devcontainer/
└── .github/workflows/
```

## セットアップ

### 前提条件

- Docker / Dev Container（推奨）
- または Python 3.12 + Node.js 20 をローカルインストール

### Dev Container で起動（推奨）

VS Code で本リポジトリを開き、「Reopen in Container」を選択してください。

コンテナ起動後、以下の3ターミナルで開発サーバーを立ち上げます。

**ターミナル1（Dev Container内）— バックエンド**

VSCode の `F5` または `Run > Start Debugging` で `Start Backend` を選択して起動。
（`.vscode/launch.json` で設定済み）

**ターミナル2（Dev Container内）— フロントエンド**

```bash
cd frontend && npm run dev
# → localhost:5173 で React 起動
```

**ターミナル3（ホストMacで）— Electron**

```bash
npm install
npm run electron:dev
# → Electron が React + FastAPI に接続して起動
```

> Electron はコンテナ内では GUI 起動できないため、ホストMac で実行します。

## 開発

### テスト

```bash
# バックエンド
cd backend && uv run pytest

# フロントエンド
cd frontend && npm run test
```

### Lint / 型チェック

```bash
# Python
uv run ruff check backend/
uv run mypy backend/

# TypeScript
cd frontend && npm run lint && npm run tsc
```

## ライセンス

MIT
