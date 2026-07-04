# infra/terraform

AWS インフラを Terraform で管理する。

- `aws/` … 環境ごとのルート構成（現状は Cognito のみ。M3 で data/backend/frontend/github-oidc を追加）
- `modules/auth/` … Cognito User Pool + Hosted UI + SPA クライアント（PKCE）
- `modules/{data,backend,frontend,github-oidc}/` … M3 で実装
- `bootstrap/` … リモートステート（S3 + DynamoDB ロック）。M3 で実装

## Cognito の作成（M2 で必要）

```bash
cd infra/terraform/aws
cp terraform.tfvars.example terraform.tfvars
# cognito_domain_prefix を一意な値に変更（例: bizx-dev-8f3a）

terraform init
terraform plan
terraform apply
```

適用後、出力値を各アプリの環境変数へ設定する:

```bash
terraform output
# cognito_user_pool_id  -> backend  BIZX_COGNITO_USER_POOL_ID
# cognito_client_id     -> backend  BIZX_COGNITO_CLIENT_ID
#                          frontend VITE_COGNITO_CLIENT_ID
# cognito_issuer        -> frontend VITE_COGNITO_AUTHORITY
```

> `terraform apply` には有効な AWS 認証情報が必要（`aws sts get-caller-identity` で確認）。
> 本番では Hosted UI の callback/logout URL に本番ドメインを追加すること。
