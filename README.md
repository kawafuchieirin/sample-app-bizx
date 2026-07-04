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

## 開発

```bash
mise install                              # ツールチェーン
cd apps/backend  && uv sync && uv run pytest
cd apps/frontend && pnpm install && pnpm test
```
