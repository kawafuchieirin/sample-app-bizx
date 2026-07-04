# infra/terraform

AWS インフラを Terraform で管理する。

## 構成

- `aws/` … 環境ごとのルート構成。以下のモジュールを束ねる:
  - `modules/auth` … Cognito User Pool + Hosted UI + SPA クライアント(PKCE)
  - `modules/data` … DynamoDB シングルテーブル(+ GSI1)
  - `modules/backend` … ECR + Lambda(コンテナ) + API Gateway(HTTP API) + IAM
  - `modules/frontend` … S3(非公開) + CloudFront(OAC) + SPA ルーティング
  - `modules/github-oidc` … GitHub OIDC プロバイダ + デプロイ用 IAM ロール
- `bootstrap/` … リモートステート(S3 + DynamoDB ロック)

## 1. リモートステート（任意・推奨）

```bash
cd infra/terraform/bootstrap
terraform init
terraform apply -var="state_bucket=bizx-tfstate-<account-id>"
```

作成後、`aws/providers.tf` に S3 バックエンドを設定して `terraform init -migrate-state`。

## 2. 本体の適用

```bash
cd infra/terraform/aws
cp terraform.tfvars.example terraform.tfvars
# cognito_domain_prefix を一意な値に、github_owner/repo を自分のリポジトリに

terraform init
terraform plan
terraform apply
```

> `terraform apply` には有効な AWS 認証情報が必要（`aws sts get-caller-identity` で確認）。
> Lambda はコンテナイメージ参照のため、**初回 apply の前に ECR へイメージを push** する必要がある
> （下記デプロイ参照。CI では push → apply の順）。

## 3. アプリへの反映

```bash
terraform output
```

| output | 設定先 |
|---|---|
| `cognito_user_pool_id` | backend `BIZX_COGNITO_USER_POOL_ID` |
| `cognito_client_id` | backend `BIZX_COGNITO_CLIENT_ID` / frontend `VITE_COGNITO_CLIENT_ID` |
| `cognito_issuer` | frontend `VITE_COGNITO_AUTHORITY` |
| `cognito_hosted_ui_domain` | frontend `VITE_COGNITO_DOMAIN` |
| `api_url` | frontend `VITE_API_BASE_URL`（`<api_url>/api/v1`） |
| `frontend_url` | frontend `VITE_REDIRECT_URI` |
| `ecr_repository_url` | CI `ECR_REPOSITORY_URL` |
| `lambda_function_name` | CI `LAMBDA_FUNCTION_NAME` |
| `frontend_bucket` | CI `FRONTEND_BUCKET` |
| `frontend_distribution_id` | CI `CLOUDFRONT_DISTRIBUTION_ID` |
| `github_deploy_role_arn` | CI secret `AWS_DEPLOY_ROLE_ARN` |

## 4. CI/CD（GitHub Actions）

- `.github/workflows/ci.yml` … PR/push で backend・frontend・terraform を検証
- `.github/workflows/deploy.yml` … main push で ECR push → Lambda 更新 → S3 sync → CloudFront invalidation

デプロイに必要な GitHub の設定（`terraform output` から一度だけ設定）:

- **Secret**: `AWS_DEPLOY_ROLE_ARN`
- **Variables**: `AWS_REGION`, `ECR_REPOSITORY_URL`, `LAMBDA_FUNCTION_NAME`, `FRONTEND_BUCKET`,
  `CLOUDFRONT_DISTRIBUTION_ID`, `API_URL`, `COGNITO_AUTHORITY`, `COGNITO_CLIENT_ID`,
  `COGNITO_DOMAIN`, `FRONTEND_URL`

### 初回デプロイ順（イメージ未 push のため）

```bash
# 1) ECR リポジトリだけ先に作る
terraform apply -target=module.backend.aws_ecr_repository.api
# 2) イメージを build & push（deploy.yml と同等の手順）
# 3) 残りを apply
terraform apply
```
