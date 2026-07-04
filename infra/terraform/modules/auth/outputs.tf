output "user_pool_id" {
  description = "Cognito User Pool ID."
  value       = aws_cognito_user_pool.this.id
}

output "client_id" {
  description = "SPA app client ID (public, PKCE)."
  value       = aws_cognito_user_pool_client.spa.id
}

output "hosted_ui_domain" {
  description = "Full Hosted UI domain."
  value       = "${aws_cognito_user_pool_domain.this.domain}.auth.${data.aws_region.current.name}.amazoncognito.com"
}

output "issuer" {
  description = "OIDC issuer URL (authority for the frontend)."
  value       = "https://cognito-idp.${data.aws_region.current.name}.amazonaws.com/${aws_cognito_user_pool.this.id}"
}

data "aws_region" "current" {}
