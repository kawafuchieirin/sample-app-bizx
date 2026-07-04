# sample-app-bizx

タスク管理 Web アプリ。React(Vite) + FastAPI + DynamoDB を AWS(Lambda/API Gateway/S3+CloudFront/Cognito) 上で動かす。

## 構成

| 領域 | 場所 | 概要 |
|---|---|---|
| フロントエンド | `apps/frontend` | React + TS + Vite、Cognito Hosted UI 認証 |
| バックエンド | `apps/backend` | FastAPI + DynamoDB、Lambda(Mangum) |
| インフラ | `infra/terraform` | Cognito / DynamoDB / Lambda / API GW / S3+CloudFront / OIDC |
| CI/CD | `.github/workflows` | CI(検証) と Deploy(OIDC) |

- 仕様: [SPEC.md](SPEC.md)
- デプロイ手順: [docs/deploy.md](docs/deploy.md)
- Secrets(sops): [docs/sops.md](docs/sops.md)

## 開発（Makefile）

主要タスクは `make` で実行できます（`make help` で一覧）。

```bash
make setup          # ツールチェーン(mise)と依存を一括セットアップ
make dev-backend    # バックエンド起動 (uvicorn :8000)
make dev-frontend   # フロント起動 (vite :5173)
make check          # CI相当の全チェック(lint + typecheck + test)
make test           # 全テスト
```

インフラ/デプロイ:

```bash
make tf-plan        # terraform plan
make tf-apply       # terraform apply
make image-push     # バックエンドimageをECRへpush
make gh-setup       # terraform outputからGitHub secret/varsを設定
make deploy         # GitHub ActionsのDeployを実行
```

> terraform/デプロイ系は `AWS_PROFILE`(既定 `workload-account`)を使用。
> 上書き例: `make tf-plan AWS_PROFILE=other`
