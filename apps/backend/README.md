# bizx backend

FastAPI + DynamoDB のタスク管理 API。

## セットアップ

```bash
cd apps/backend
uv sync                 # 依存インストール（.venv 作成）
cp .env.example .env    # ローカル設定（BIZX_AUTH_DISABLED=true で認証をバイパス）
```

共有 secret は sops で暗号化した `apps/backend/.env.sops` に置きます。
初期設定と復号手順は [docs/sops.md](../../docs/sops.md) を参照してください。

## 開発サーバー

```bash
uv run uvicorn app.main:app --reload --port 8000
# ヘルスチェック: http://localhost:8000/api/v1/health
# OpenAPI:       http://localhost:8000/docs
```

DynamoDB はローカル（docker の amazon/dynamodb-local）または AWS を利用。
ローカル DynamoDB を使う場合:

```bash
BIZX_DYNAMODB_ENDPOINT_URL=http://localhost:8000 uv run python -m app.scripts.create_table
```

## 品質チェック

```bash
uv run pytest        # テスト（moto で DynamoDB をモック）
uv run ruff check .  # Lint
uv run ruff format . # 整形
uv run mypy app      # 型チェック（strict）
```

## 認証

- 本番: Cognito 発行の JWT を JWKS で検証（`BIZX_COGNITO_USER_POOL_ID` / `BIZX_COGNITO_CLIENT_ID`）
- ローカル/テスト: `BIZX_AUTH_DISABLED=true` で署名検証をスキップし、トークンの `sub` を信頼
  （**デプロイ環境では絶対に true にしない**）

## API

`/api/v1` 配下。`GET /health` 以外は Bearer トークン必須。ボード / タスクの CRUD は
[SPEC.md](../../SPEC.md) の「API 設計」を参照。

## デプロイ（AWS Lambda）

`Mangum` で FastAPI を Lambda 化し、API Gateway HTTP API 経由で公開する
（ハンドラ: `app.lambda_handler.handler`）。コンテナイメージとして ECR に push:

```bash
docker build -t <ecr_repository_url>:latest .   # context = apps/backend
docker push <ecr_repository_url>:latest
aws lambda update-function-code \
  --function-name <lambda_function_name> \
  --image-uri <ecr_repository_url>:latest
```

インフラ(ECR/Lambda/API GW/IAM)は [infra/terraform](../../infra/terraform/README.md) の
`modules/backend`。CI では `.github/workflows/deploy.yml` が自動化する。
