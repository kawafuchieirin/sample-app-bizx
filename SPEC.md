# SPEC — sample-app-bizx（タスク管理アプリ）

> 本ドキュメントは実装フェーズの単一の情報源（Source of Truth）。
> Plan Mode で計画し、本 SPEC を新規セッションで実装に落とす（SDD パターン）。

---

## 1. 概要

複数ユーザーがそれぞれログインして、自分のタスクをボード（カンバン）形式で管理する Web アプリ。
タスクには期限・優先度・ステータスを設定でき、ステータス列（ToDo / 進行中 / 完了）をまたいで管理する。

- **プロダクト段階**: MVP
- **ゴール**: ログインしたユーザーが、ボード上でタスクを作成・編集・移動・削除でき、期限と優先度で状況を把握できる状態
- **非ゴール（今回やらない）**: チーム共有、タスクの相互割り当て、ラベル/全文検索、通知、コメント、添付ファイル

---

## 2. スコープ

### 2.1 対象（In Scope / MVP）
- 認証（サインアップ / ログイン / ログアウト）— 各ユーザーは自分のデータのみ参照・操作可能
- ボード CRUD（1ユーザーが複数ボードを持てる）
- タスク CRUD（作成・一覧・編集・削除）
- タスク属性: タイトル、説明、ステータス、優先度（高/中/低）、期限（任意）
- ステータス管理: `todo` / `in_progress` / `done`、カンバン列間の移動
- 一覧のフィルタ・並び替え（ステータス別表示、期限・優先度でのソート）

### 2.2 対象外（Out of Scope / 将来対応）
- チーム/ボード共有、メンバー招待、権限ロール
- ラベル/タグ、キーワード検索
- 期限通知・リマインダー、メール送信
- コメント、履歴、添付ファイル
- サブタスク、繰り返しタスク

---

## 3. 想定ユーザー / 主要ユースケース

- **個人ユーザー**: 自分の仕事・私用タスクをボードで整理したい
  1. サインアップしてログインする
  2. ボードを作る（例: 「仕事」「家事」）
  3. タスクを追加し、期限・優先度を設定する
  4. 進捗に応じてタスクを `todo → in_progress → done` へ移動する
  5. 期限や優先度で並び替えて、今やるべきことを把握する

---

## 4. 技術スタック（確定済み）

| レイヤー | 技術 |
|---|---|
| フロントエンド | React + TypeScript + Vite（pnpm） / テスト: Vitest + Testing Library / Lint: ESLint |
| バックエンド | FastAPI + Python 3.13（uv） / Lint: ruff / 型: mypy / テスト: pytest / AWSモック: moto |
| データストア | Amazon DynamoDB（シングルテーブル設計） |
| 認証 | Amazon Cognito User Pool（JWT 検証） |
| インフラ | AWS + Terraform（modules: frontend / backend / data / github-oidc） |
| CI/CD | GitHub Actions + GitHub OIDC（AWSへ keyless デプロイ） |

---

## 5. アーキテクチャ

```
[Browser] ──HTTPS──> [CloudFront + S3]        ← フロント（静的配信: Vite build 成果物）
     │
     │  API (fetch, JWT Bearer)
     ▼
[API Gateway / ALB] ──> [FastAPI (Lambda or ECS/Fargate)]
     │                         │
     │  認証(JWT検証)          │  DynamoDB SDK
     ▼                         ▼
[Cognito User Pool]      [DynamoDB (single table)]
```

- フロントは静的ホスティング（S3 + CloudFront）。API は別オリジンで CORS 設定。
- 認証は Cognito 発行の JWT を `Authorization: Bearer` で送信し、FastAPI 側で検証（`sub` をユーザーID として利用）。
- バックエンドの実行基盤（Lambda / Fargate）は infra 実装時に確定（§11 の要確認事項）。

---

## 6. データモデル（DynamoDB シングルテーブル）

テーブル名: `bizx-tasks`（環境ごとにサフィックス）

### 6.1 アクセスパターン
1. あるユーザーのボード一覧を取得
2. あるボードのタスク一覧を取得
3. あるユーザーのタスクをステータス別に取得し、期限順で並べる
4. タスク単体の取得・更新・削除

### 6.2 キー設計

| エンティティ | PK | SK | GSI1PK | GSI1SK | 主な属性 |
|---|---|---|---|---|---|
| Board | `USER#{userId}` | `BOARD#{boardId}` | — | — | name, created_at, updated_at |
| Task | `USER#{userId}` | `TASK#{taskId}` | `BOARD#{boardId}` | `STATUS#{status}#DUE#{dueDate}#{taskId}` | board_id, title, description, status, priority, due_date, created_at, updated_at |

> タスクは**ユーザーのパーティション（`USER#{userId}`）**に置き、`taskId` 単体で O(1) 取得・所有者スコープを両立。
> ボード単位の一覧は **GSI1（`GSI1PK=BOARD#{boardId}`）** で取得する。期限未設定は番兵値 `9999-12-31` で末尾ソート。

- パターン1（ユーザーのボード一覧）: `Query PK=USER#{userId} AND begins_with(SK, "BOARD#")`
- パターン2（タスク単体の取得/更新/削除）: `GetItem PK=USER#{userId}, SK=TASK#{taskId}`
- パターン3（ボードのタスク一覧・ステータス絞込・期限順）: `Query GSI1 GSI1PK=BOARD#{boardId} [AND begins_with(GSI1SK, "STATUS#{status}#")]`

### 6.3 属性の値域
- `status`: `todo` | `in_progress` | `done`
- `priority`: `high` | `medium` | `low`
- `dueDate`: ISO8601（`YYYY-MM-DD`）または null
- ID: ULID または UUIDv4（時系列ソート性から ULID 推奨）
- タイムスタンプ: ISO8601 UTC

---

## 7. API 設計（FastAPI）

ベースパス: `/api/v1` — 全エンドポイントで JWT 認証必須（`sub` = userId）。

| メソッド | パス | 説明 |
|---|---|---|
| GET | `/health` | ヘルスチェック（認証不要） |
| GET | `/boards` | 自分のボード一覧 |
| POST | `/boards` | ボード作成 |
| PATCH | `/boards/{boardId}` | ボード更新（名称） |
| DELETE | `/boards/{boardId}` | ボード削除（配下タスクも削除） |
| GET | `/boards/{boardId}/tasks` | ボード内タスク一覧（`?status=`, `?sort=due|priority`） |
| POST | `/boards/{boardId}/tasks` | タスク作成 |
| GET | `/tasks/{taskId}` | タスク取得 |
| PATCH | `/tasks/{taskId}` | タスク更新（属性・ステータス移動） |
| DELETE | `/tasks/{taskId}` | タスク削除 |

- リクエスト/レスポンスは Pydantic モデルで定義（`app/api` にスキーマ）。
- 認可: リソースの `userId` とトークンの `sub` を照合し、不一致は `403`。
- エラー: `400`（バリデーション）/ `401`（未認証）/ `403`（他人のリソース）/ `404`（存在しない）を明確なメッセージで返す。

---

## 8. フロントエンド構成

- ルーティング: ログイン / ボード一覧 / ボード詳細（カンバン）
- 主要画面
  - **ログイン/サインアップ**: Cognito 連携
  - **ボード一覧**: ボードの作成・削除・選択
  - **カンバンボード**: 3列（ToDo / 進行中 / 完了）、タスクカードの作成・編集・列移動・削除
- 状態管理・データ取得: fetch ラッパー（JWT 付与）＋軽量な状態管理（MVP は最小限）
- フィルタ/ソート UI: ステータス列表示、期限・優先度ソート

---

## 9. 非機能要件

- **セキュリティ**: JWT 検証必須、他ユーザーのデータへアクセス不可、シークレットは環境変数/SSM 管理（ハードコード禁止）
- **入力検証**: 全外部入力を Pydantic で検証（最小権限）
- **テスト**: バックエンドは pytest + moto で DynamoDB をモックし、CRUD・認可・エッジケースをカバー。フロントは Vitest + Testing Library で主要フローをテスト
- **品質ゲート**: ruff / mypy / ESLint / 各テストを CI で必須化
- **エラーハンドリング**: 握りつぶし禁止。DynamoDB 呼び出しは失敗前提（タイムアウト/リトライ）
- **パフォーマンス**: 一覧取得は N+1 を避け、GSI で 1 クエリ取得

---

## 10. マイルストーン / タスク分解

### M0: 基盤整備
- [ ] `.gitignore` 整備（`.venv` / `node_modules` / `.terraform` / cache 類を除外）
- [ ] `.mise.toml` で node / python / terraform のバージョン固定
- [ ] モノレポの scaffold を git 管理下に（現状 README のみ tracked）

### M1: バックエンド MVP
- [ ] DynamoDB アクセス層（シングルテーブル、リポジトリパターン）
- [ ] Board / Task の Pydantic スキーマ
- [ ] CRUD エンドポイント実装
- [ ] JWT 認証ミドルウェア（Cognito JWKS 検証）＋ 認可
- [ ] pytest + moto でのテスト

### M2: フロントエンド MVP
- [ ] Cognito ログイン/サインアップ
- [ ] ボード一覧画面
- [ ] カンバンボード（タスク CRUD・列移動）
- [ ] フィルタ/ソート
- [ ] Vitest テスト

### M3: インフラ / CI-CD
- [ ] Terraform: data(DynamoDB) / backend / frontend / github-oidc
- [ ] GitHub Actions（lint → test → build → deploy、OIDC）

---

## 11. 要確認事項

### 確定済み
- **認証（ログイン方式）**: ✅ Cognito **Hosted UI**（OAuth2 Authorization Code + PKCE）
- **ID 方式**: ✅ ULID
- **環境**: ✅ dev / prod の 2 環境
- **Cognito 構築**: ✅ Terraform `modules/auth`（Hosted UI・SPA クライアント）を M2 で前倒し実装

### 未確定（M3 デプロイ時に確定）
1. **バックエンド実行基盤**: Lambda（サーバーレス）か ECS/Fargate か → コスト/コールドスタートで判断
2. **API 公開方式**: API Gateway か ALB か
3. **ボードの初期体験**: サインアップ時にデフォルトボードを自動作成するか
4. **Terraform リモートステート**: `bootstrap`（S3 + DynamoDB ロック）の構築
```
