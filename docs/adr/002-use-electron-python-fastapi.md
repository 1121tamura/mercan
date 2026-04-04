# ADR 002: デスクトップ + バックエンドに Electron + Python + FastAPI を採用する

## ステータス

採用

## 決定日

2025-04-04

---

## コンテキスト

デスクトップアプリのシェルとバックエンドの技術選定において、以下の組み合わせを検討した。

| 構成 | デスクトップ | バックエンド |
|---|---|---|
| A | Electron | Python + FastAPI |
| B | Tauri | Go + Huma |

---

## 決定

**Electron + Python + FastAPI** を採用する。

---

## 理由

### DDD + Clean Architectureの実装しやすさ

| 観点 | Python + FastAPI | Go + Huma |
|---|---|---|
| 依存性注入（DI） | ◎ FastAPI標準機能で強力 | △ 自前実装が必要 |
| 依存性逆転（DIP） | ◎ Protocol / ABCで直感的 | ○ interfaceで書けるが冗長 |
| リポジトリパターン | ◎ | ○ |
| DDD日本語リソース | ◎ 豊富 | △ 少なめ |

FastAPIの依存性注入（DI）機能がClean Architectureと相性が良く、
Python + FastAPIの方がDDD + Clean Architectureを自然に実装できる。

### トレードオフの許容

以下のデメリットは認識した上で採用を決定する。

| デメリット | 内容 |
|---|---|
| バイナリサイズ | PyInstaller込みで100MB超になる |
| 起動速度 | Pythonプロセス起動に数秒かかる |

---

## 却下した選択肢

### Tauri + Go + Huma
- バイナリが軽量（20〜40MB）・起動が高速という利点がある
- ただしGoはDI機能が標準でなく自前実装が必要
- DDD + Clean Architectureの実装が冗長になりやすい
- Go + DDDの日本語学習リソースが少ない
