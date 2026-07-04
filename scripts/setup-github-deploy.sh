#!/usr/bin/env bash
#
# Configure the GitHub Actions secret/variables that .github/workflows/deploy.yml
# needs, reading values straight from `terraform output`.
#
# Prerequisites: infra applied (terraform apply), gh CLI logged in, run from repo.
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TF_DIR="$ROOT/infra/terraform/aws"

command -v gh >/dev/null || { echo "gh CLI is required"; exit 1; }
command -v terraform >/dev/null || { echo "terraform is required"; exit 1; }

out() { terraform -chdir="$TF_DIR" output -raw "$1"; }

echo "Reading terraform outputs from $TF_DIR ..."
ROLE_ARN="$(out github_deploy_role_arn)"

echo "Setting secret AWS_DEPLOY_ROLE_ARN ..."
gh secret set AWS_DEPLOY_ROLE_ARN --body "$ROLE_ARN"

echo "Setting repository variables ..."
gh variable set AWS_REGION                 --body "$(out region)"
gh variable set ECR_REPOSITORY_URL         --body "$(out ecr_repository_url)"
gh variable set LAMBDA_FUNCTION_NAME       --body "$(out lambda_function_name)"
gh variable set FRONTEND_BUCKET            --body "$(out frontend_bucket)"
gh variable set CLOUDFRONT_DISTRIBUTION_ID --body "$(out frontend_distribution_id)"
gh variable set API_URL                    --body "$(out api_url)"
gh variable set COGNITO_AUTHORITY          --body "$(out cognito_issuer)"
gh variable set COGNITO_CLIENT_ID          --body "$(out cognito_client_id)"
gh variable set COGNITO_DOMAIN             --body "$(out cognito_hosted_ui_domain)"
gh variable set FRONTEND_URL               --body "$(out frontend_url)"

echo
echo "Done. Verify with: gh variable list && gh secret list"
echo "Enable auto-deploy on push to main with:"
echo "  gh variable set DEPLOY_ENABLED --body true"
