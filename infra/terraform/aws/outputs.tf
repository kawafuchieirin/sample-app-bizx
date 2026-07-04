output "cognito_user_pool_id" {
  description = "Set as BIZX_COGNITO_USER_POOL_ID (backend)."
  value       = module.auth.user_pool_id
}

output "cognito_client_id" {
  description = "Set as BIZX_COGNITO_CLIENT_ID (backend) and VITE_COGNITO_CLIENT_ID (frontend)."
  value       = module.auth.client_id
}

output "cognito_issuer" {
  description = "Set as VITE_COGNITO_AUTHORITY (frontend)."
  value       = module.auth.issuer
}

output "cognito_hosted_ui_domain" {
  description = "Cognito Hosted UI domain."
  value       = module.auth.hosted_ui_domain
}
