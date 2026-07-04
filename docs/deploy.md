# デプロイ手順書

AWS へ初回デプロイし、GitHub Actions の自動デプロイを有効化するまでの手順。

## 前提

- 有効な AWS 認証情報（`aws sts get-caller-identity` が成功すること）
- `terraform` / `docker` / `aws` / `gh` / `pnpm` / `uv`（`mise install` で導入）
- gh CLI ログイン済み（`repo`, `workflow` スコープ）

## 0. AWS 認証

```bash
aws sts get-caller-identity   # まず確認
```

`InvalidClientTokenId` / `ExpiredToken` の場合は認証をやり直す:

- SSO を使う場合: `aws sso login --profile <profile>`（`export AWS_PROFILE=<profile>`）
- IAM アクセスキーの場合: `aws configure`（有効なキーに更新）

> このセッションで対話ログインが必要なら、プロンプトに `! aws sso login` のように
> `!` を付けて実行すると、出力をこの会話に取り込めます。

## 1. （推奨）リモートステート

```bash
cd infra/terraform/bootstrap
terraform init
terraform apply -var="state_bucket=bizx-tfstate-<account-id>"
```

作成後、`infra/terraform/aws/providers.tf` に S3 backend を追記し `terraform init -migrate-state`。
（スキップしてローカルステートのまま進めても可）

## 2. 変数の準備

```bash
cd infra/terraform/aws
cp terraform.tfvars.example terraform.tfvars
# cognito_domain_prefix … グローバル一意な値に（例: bizx-dev-8f3a）
# github_owner / github_repo … 自分のリポジトリに
terraform init
```

## 3. 初回 apply（ECR → イメージ push → 本適用）

Lambda はコンテナイメージ参照のため、**イメージが ECR に存在してから** Lambda を作る。

```bash
# 3-1. ECR リポジトリだけ先に作成
terraform apply -target=module.backend.aws_ecr_repository.api

# 3-2. イメージを build & push（Lambda 未作成なので push のみ実行される）
../../../scripts/push-backend-image.sh

# 3-3. 残り全部を適用（Lambda / API GW / DynamoDB / CloudFront / Cognito / IAM）
terraform apply
```

## 4. GitHub の secret/vars を設定（自動）

```bash
# リポジトリルートで
./scripts/setup-github-deploy.sh
gh variable list && gh secret list   # 確認
```

## 5. フロントを配信

```bash
# 自動デプロイを有効化（以降 main への push で deploy.yml が走る）
gh variable set DEPLOY_ENABLED --body true

# 今すぐ手動でデプロイする場合:
gh workflow run Deploy
```

## 6. 動作確認

1. `terraform output frontend_url` の URL を開く
2. 「ログイン」→ Cognito Hosted UI でサインアップ（メール確認）→ ログイン
3. ボード作成 → タスク作成 → 列移動、が API 経由で保存されることを確認

---

## ローカルで動かす場合（AWS 上のバックエンドを使う）

```bash
cd apps/frontend
cp .env.example .env.local
# terraform output の値を設定（cognito_issuer / client_id / hosted_ui_domain /
#   api_url(+/api/v1) / frontend_url は http://localhost:5173/）
pnpm dev
```

---

## よくあるエラーと対処

| 症状 | 原因 | 対処 |
|---|---|---|
| `InvalidClientTokenId` / `ExpiredToken` | AWS 認証切れ | 手順0で再認証 |
| Cognito `domain already exists` | `cognito_domain_prefix` が他アカウントと衝突 | 一意な値に変更して再 apply |
| 初回 apply で `Source image ... does not exist` / `ImageNotFound` | 手順3-1/3-2を飛ばした | ECR 作成 → `push-backend-image.sh` → `terraform apply` |
| OIDC `EntityAlreadyExists`（provider 重複） | アカウントに既に GitHub OIDC provider がある | `terraform.tfvars` に `create_oidc_provider = false` |
| Lambda 更新で `architecture` エラー | イメージが arm64 等で不一致 | `push-backend-image.sh`（`--platform linux/amd64`）で再 push |
| ログイン後 API が 403 | CORS/監査。CloudFront ドメインが許可されていない等 | `terraform output` 後の CORS 反映（backend 再 apply）、トークンの client_id を確認 |
| CI Deploy が `AccessDenied`（S3/ECR） | secret/vars 未設定、または OIDC ロール権限 | `setup-github-deploy.sh` 実行、`DEPLOY_ENABLED=true` を確認 |
| ブラウザに反映されない | CloudFront 伝播待ち | 数分待つ / `create-invalidation` は deploy.yml が自動実行 |

> apply でエラーが出たら、そのメッセージ全文を貼ってください。原因特定と修正を一緒に進めます。
