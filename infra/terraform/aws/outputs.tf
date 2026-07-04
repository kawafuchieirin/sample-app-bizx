# --- Cognito (backend + frontend env) ------------------------------------

output "cognito_user_pool_id" {
  description = "Set as BIZX_COGNITO_USER_POOL_ID (backend)."
  value       = module.auth.user_pool_id
}

output "cognito_client_id" {
  description = "BIZX_COGNITO_CLIENT_ID (backend) and VITE_COGNITO_CLIENT_ID (frontend)."
  value       = module.auth.client_id
}

output "cognito_issuer" {
  description = "VITE_COGNITO_AUTHORITY (frontend)."
  value       = module.auth.issuer
}

output "cognito_hosted_ui_domain" {
  description = "VITE_COGNITO_DOMAIN (frontend)."
  value       = module.auth.hosted_ui_domain
}

# --- Data ----------------------------------------------------------------

output "table_name" {
  value = module.data.table_name
}

# --- Backend (API) -------------------------------------------------------

output "api_url" {
  description = "HTTP API base URL. VITE_API_BASE_URL = <api_url>/api/v1."
  value       = module.backend.api_url
}

output "ecr_repository_url" {
  description = "Push the backend Lambda image here."
  value       = module.backend.ecr_repository_url
}

output "lambda_function_name" {
  value = module.backend.lambda_function_name
}

# --- Frontend (hosting) --------------------------------------------------

output "frontend_bucket" {
  description = "S3 bucket to sync the built SPA into."
  value       = module.frontend.bucket_name
}

output "frontend_distribution_id" {
  value = module.frontend.distribution_id
}

output "frontend_url" {
  value = module.frontend.url
}

# --- CI/CD ---------------------------------------------------------------

output "github_deploy_role_arn" {
  description = "Set as GitHub secret AWS_DEPLOY_ROLE_ARN."
  value       = module.github_oidc.deploy_role_arn
}
