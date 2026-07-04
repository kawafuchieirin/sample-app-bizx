# bizx frontend

React + TypeScript + Vite。Cognito Hosted UI（OAuth2 Authorization Code + PKCE）で認証し、
バックエンドAPIに対してボード/タスクを操作するSPA。

## セットアップ

```bash
cd apps/frontend
pnpm install
cp .env.example .env.local   # terraform output の値を設定
```

`.env.local` に設定する値（`infra/terraform/aws` の `terraform output` から取得）:

| 変数 | 由来 |
|---|---|
| `VITE_COGNITO_AUTHORITY` | `cognito_issuer` |
| `VITE_COGNITO_CLIENT_ID` | `cognito_client_id` |
| `VITE_COGNITO_DOMAIN` | `cognito_hosted_ui_domain` |
| `VITE_REDIRECT_URI` | `http://localhost:5173/`（Terraform の callback_urls と一致） |
| `VITE_API_BASE_URL` | バックエンドAPI（例: `http://localhost:8000/api/v1`） |

## 開発

```bash
pnpm dev         # http://localhost:5173
pnpm typecheck   # tsc --noEmit
pnpm lint        # eslint
pnpm test        # vitest（API/認証はモック）
pnpm build       # 本番ビルド（dist/）
```

## 認証フロー

1. 未ログイン時は「ログイン」ボタン → Cognito Hosted UI にリダイレクト
2. ログイン成功で `VITE_REDIRECT_URI` に戻り、`react-oidc-context` が code を処理
3. 以降、API 呼び出しに access token を `Authorization: Bearer` で付与
4. ログアウトは Cognito の `/logout` へリダイレクト（`src/auth/oidc.ts`）

> ローカルでフロントを動かすには、先に `infra/terraform/aws` で Cognito を作成し、
> 出力値を `.env.local` に設定する必要があります（[infra/terraform/README.md](../../infra/terraform/README.md)）。

## 画面

- `/` … ボード一覧（作成・削除）
- `/boards/:boardId` … カンバン（ToDo / 進行中 / 完了、タスク作成・列移動・削除）
