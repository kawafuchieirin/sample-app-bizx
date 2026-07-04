#!/usr/bin/env bash
#
# Build the backend Lambda image and push it to ECR, then update the Lambda.
# Useful for the first apply (image must exist before the Lambda is created)
# and for manual redeploys.
#
# Usage: scripts/push-backend-image.sh [image_tag]   (default tag: latest)
#
# Lambda is x86_64, so we always build linux/amd64 (emulated on Apple Silicon).
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TF_DIR="$ROOT/infra/terraform/aws"
TAG="${1:-latest}"

command -v aws >/dev/null || { echo "aws CLI is required"; exit 1; }
command -v docker >/dev/null || { echo "docker is required"; exit 1; }

ECR_URL="$(terraform -chdir="$TF_DIR" output -raw ecr_repository_url)"
REGION="$(terraform -chdir="$TF_DIR" output -raw region)"
REGISTRY="${ECR_URL%%/*}"

echo "Logging in to ECR ($REGISTRY) ..."
aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

echo "Building $ECR_URL:$TAG (linux/amd64) ..."
docker build --platform linux/amd64 -t "$ECR_URL:$TAG" "$ROOT/apps/backend"

echo "Pushing ..."
docker push "$ECR_URL:$TAG"

# Update the Lambda if it already exists (skipped on the very first apply).
LAMBDA="$(terraform -chdir="$TF_DIR" output -raw lambda_function_name 2>/dev/null || true)"
if [ -n "${LAMBDA:-}" ]; then
  echo "Updating Lambda $LAMBDA ..."
  aws lambda update-function-code \
    --function-name "$LAMBDA" \
    --image-uri "$ECR_URL:$TAG" \
    --region "$REGION" >/dev/null
  echo "Lambda updated."
else
  echo "Lambda not created yet — run 'terraform apply' now."
fi
