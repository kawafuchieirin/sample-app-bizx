# sample-app-bizx — 開発・デプロイ用タスク
#
# 使い方: `make` または `make help` でコマンド一覧を表示。
# 変数は上書き可: 例) make tf-plan AWS_PROFILE=other-profile

BACKEND  := apps/backend
FRONTEND := apps/frontend
TF       := infra/terraform/aws

# AWS(SSO)プロファイル。terraform/デプロイ系で使用。環境に合わせて上書き可。
AWS_PROFILE ?= workload-account
export AWS_PROFILE

.DEFAULT_GOAL := help

.PHONY: help
help: ## このヘルプを表示
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------- セットアップ

.PHONY: doctor setup install install-backend install-frontend
doctor: ## 必要ツールが揃っているか確認(初回はまずこれ)
	@echo "必須ツール:"
	@for t in mise uv pnpm node; do \
		if command -v $$t >/dev/null 2>&1; then printf "  \033[32m✓\033[0m %s\n" "$$t"; \
		else printf "  \033[31m✗ %s が見つかりません\033[0m\n" "$$t"; fi; \
	done
	@echo "デプロイ用(任意):"
	@for t in terraform docker gh aws; do \
		if command -v $$t >/dev/null 2>&1; then printf "  \033[32m✓\033[0m %s\n" "$$t"; \
		else printf "  \033[33m-\033[0m %s (未導入)\n" "$$t"; fi; \
	done
	@echo "未導入のものは docs/onboarding.md を参照。多くは 'mise install' で入ります。"

setup: ## ツールチェーン(mise)と依存を一括セットアップ
	mise install
	$(MAKE) install

install: install-backend install-frontend ## 依存をインストール

install-backend: ## バックエンド依存(uv sync)
	cd $(BACKEND) && uv sync

install-frontend: ## フロント依存(pnpm install)
	cd $(FRONTEND) && pnpm install

# ------------------------------------------------------------------------ 開発

.PHONY: dev-backend dev-frontend
dev-backend: ## バックエンドをローカル起動 (uvicorn :8000)
	cd $(BACKEND) && uv run uvicorn app.main:app --reload --port 8000

dev-frontend: ## フロントをローカル起動 (vite :5173)
	cd $(FRONTEND) && pnpm dev

# ------------------------------------------------------------------------ 品質

.PHONY: check test test-backend test-frontend lint format typecheck build
check: lint typecheck test ## CI相当の全チェック(lint+typecheck+test)

test: test-backend test-frontend ## 全テスト

test-backend: ## バックエンドテスト(pytest)
	cd $(BACKEND) && uv run pytest

test-frontend: ## フロントテスト(vitest)
	cd $(FRONTEND) && pnpm test

lint: ## Lint(ruff + eslint)
	cd $(BACKEND) && uv run ruff check .
	cd $(FRONTEND) && pnpm lint

format: ## 整形(ruff format)
	cd $(BACKEND) && uv run ruff format .

typecheck: ## 型チェック(mypy + tsc)
	cd $(BACKEND) && uv run mypy app
	cd $(FRONTEND) && pnpm typecheck

build: ## フロント本番ビルド
	cd $(FRONTEND) && pnpm build

# ---------------------------------------------------------------- インフラ/CD

.PHONY: tf-init tf-plan tf-apply tf-output image-push gh-setup deploy
tf-init: ## terraform init
	terraform -chdir=$(TF) init

tf-plan: ## terraform plan
	terraform -chdir=$(TF) plan

tf-apply: ## terraform apply
	terraform -chdir=$(TF) apply

tf-output: ## terraform output
	terraform -chdir=$(TF) output

image-push: ## バックエンドimageをECRへpush(+Lambda更新)
	./scripts/push-backend-image.sh

gh-setup: ## terraform outputからGitHub secret/varsを設定
	./scripts/setup-github-deploy.sh

deploy: ## GitHub ActionsのDeployワークフローを実行
	gh workflow run Deploy

# ------------------------------------------------------------------ クリーン

.PHONY: clean
clean: ## ビルド成果物/キャッシュを削除
	rm -rf $(FRONTEND)/dist $(FRONTEND)/.vite
	find $(BACKEND) -type d -name __pycache__ -prune -exec rm -rf {} +
