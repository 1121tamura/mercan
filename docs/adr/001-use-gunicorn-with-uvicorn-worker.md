# ADR 001: ASGIサーバーに gunicorn + uvicornワーカーを採用する

## ステータス

採用

## 決定日

2025-04-04

---

## コンテキスト

FastAPIアプリケーションを動かすASGIサーバーの選定が必要だった。
候補として以下を検討した。

| 候補 | 特徴 |
|---|---|
| uvicorn単体 | シンプル・軽量。ただしシングルプロセス |
| gunicorn + uvicornワーカー | マルチプロセス管理が可能 |
| uWSGI | WSGI専用のためASGI（非同期）機能が使えない |

---

## 決定

**gunicorn + uvicornワーカー** を採用する。

起動コマンド：
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

`pyproject.toml` には両方を依存パッケージとして追加する：
- `gunicorn`：マルチプロセス管理
- `uvicorn`：ASGIワーカー（gunicornのワーカーとして動作）

---

## 理由

- 家族など複数人での同時利用の可能性がある
- gunicornのマルチプロセスにより、同時リクエストを複数ワーカーで処理できる
- uvicorn単体ではシングルプロセスのため、複数人利用時にリクエストが詰まる恐れがある

---

## 環境別の使い分け

| 環境 | サーバー | 理由 |
|---|---|---|
| **開発時** | uvicorn（`--reload`） | 自動リロードが効く・デバッグしやすい |
| **本番** | gunicorn + uvicornワーカー | マルチプロセスで複数人利用に対応 |

### 開発時の起動コマンド
```bash
uvicorn main:app --reload --port 8000
```

### 本番の起動コマンド
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 却下した選択肢

### uvicorn単体
- シングルプロセスのため複数人利用に不向き
- 1人専用のユースケースであれば十分だが、今回は採用しない

### uWSGI
- WSGI専用のためFastAPIのASGI・非同期機能を活かせない
