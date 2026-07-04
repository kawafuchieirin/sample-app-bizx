# オンボーディング（はじめての方へ）

このプロジェクトに初めて触れる人向けの「地図」です。専門用語もかみ砕いて説明します。

## これは何のアプリ？

**タスク管理アプリ**です。ユーザーがログインして、自分のタスクを
「ToDo / 進行中 / 完了」のボード（カンバン）で管理できます。

## 全体像（ざっくり）

```
[あなたのブラウザ]
      │  ①画面を表示
      ▼
[CloudFront + S3] ← フロントエンド（React）。見た目の部分。
      │  ②ログイン/API呼び出し
      ├───────────────► [Cognito] ← ログイン画面と認証を担当
      │  ③データの読み書き（ログイン後）
      ▼
[API Gateway → Lambda(FastAPI)] ← バックエンド。処理のルール。
      │
      ▼
[DynamoDB] ← データの保管庫（ボード・タスク）
```

- **フロントエンド** = 画面（ボタンや一覧など、目に見える部分）
- **バックエンド** = 裏側の処理（「タスクを保存する」などのルール）
- **データベース(DynamoDB)** = 情報の保管庫

## ディレクトリ構成

| 場所 | 中身 |
|---|---|
| `apps/frontend` | 画面（React + TypeScript + Vite） |
| `apps/backend` | API（Python + FastAPI） |
| `infra/terraform` | AWS の構成（コードでインフラを定義） |
| `.github/workflows` | CI/CD（自動テスト・自動デプロイ） |
| `scripts` | 補助スクリプト |
| `docs` | ドキュメント |
| `SPEC.md` | 仕様書（何を作るかの決めごと） |

## 初日の流れ

```bash
git clone https://github.com/kawafuchieirin/sample-app-bizx.git
cd sample-app-bizx

make doctor    # 必要ツールの確認
make setup     # ツール＆依存のセットアップ
make test      # 全テストが通るか確認（緑ならOK）
make dev-frontend   # 画面を起動 → http://localhost:5173
```

うまくいったら、[CONTRIBUTING.md](../CONTRIBUTING.md) の「変更を加える流れ」へ。

## ツールの導入

`mise` がツール（Node/Python/Terraform 等）のバージョンをまとめて管理します。

```bash
# mise が無い場合（macOS/Homebrew の例）
brew install mise
# シェル設定に追記（zsh の例）: eval "$(mise activate zsh)"

mise install   # .mise.toml のツールを一括インストール
```

- **pnpm** … フロントのパッケージ管理（npm の高速版）
- **uv** … Python の依存管理（pip の高速版）
- どちらも `mise install` で入ります

## 用語集（かみ砕いて）

| 用語 | ひとことで |
|---|---|
| **React / Vite** | 画面を作るための道具（部品を組み合わせて UI を作る） |
| **FastAPI** | Python で API（裏側の処理窓口）を作る道具 |
| **API** | フロントとバックエンドの「注文窓口」。決まった形でやり取りする |
| **DynamoDB** | AWS のデータベース。ボードやタスクを保存する場所 |
| **AWS Lambda** | サーバーを常時立てず、呼ばれた時だけ動く実行環境 |
| **API Gateway** | 外からの API リクエストを Lambda につなぐ入口 |
| **S3** | ファイル置き場。ここにフロントの完成品を置く |
| **CloudFront** | 世界中に速く配信する仕組み（S3 の前に立つ） |
| **Cognito** | ログイン・ユーザー管理を任せる AWS のサービス |
| **Hosted UI** | Cognito が用意する既製のログイン画面 |
| **PKCE / OAuth** | 安全にログインするための手順（合言葉の受け渡し方） |
| **JWT / トークン** | ログイン済みを証明する「通行証」。API 呼び出しに添える |
| **Terraform** | AWS の構成を**コードで**定義・作成する道具 |
| **OIDC** | GitHub から AWS へ、鍵を保存せず安全に認証する仕組み |
| **CI/CD** | 変更のたびに自動でテスト(CI)・自動で公開(CD) |
| **Mangum** | FastAPI を Lambda で動かすための橋渡し |
| **モノレポ** | フロント/バック/インフラを1つのリポジトリで管理する構成 |

## よくあるつまずき

| 症状 | 対処 |
|---|---|
| `make: command not found` | Xcode Command Line Tools を入れる: `xcode-select --install` |
| `make doctor` で必須ツールが ✗ | `mise install`。mise 自体が無ければ上記「ツールの導入」 |
| `pnpm dev` で画面は出るがログインできない | `apps/frontend/.env.local` が必要。[docs/deploy.md](deploy.md) 参照 |
| テストは通るのに API がエラー | ローカルでバックエンドを動かす設定が必要（方式B、[docs/deploy.md](deploy.md)） |

わからないことは、遠慮なく Issue で質問してください。「何が分からないか分からない」段階の質問も歓迎です。
