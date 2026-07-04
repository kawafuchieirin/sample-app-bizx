variable "region" {
  description = "AWS region."
  type        = string
  default     = "ap-northeast-1"
}

variable "environment" {
  description = "Deployment environment (dev, prod, ...)."
  type        = string
  default     = "dev"
}

variable "cognito_domain_prefix" {
  description = "Globally-unique Cognito Hosted UI domain prefix (e.g. bizx-dev-1234)."
  type        = string
}

variable "backend_image_tag" {
  description = "ECR image tag for the backend Lambda. CI pushes this before apply."
  type        = string
  default     = "latest"
}

variable "github_owner" {
  description = "GitHub org/user that owns the repo (for OIDC deploy role)."
  type        = string
}

variable "github_repo" {
  description = "Repository name (for OIDC deploy role)."
  type        = string
  default     = "sample-app-bizx"
}

variable "create_oidc_provider" {
  description = "Create the GitHub OIDC provider (false if it already exists in the account)."
  type        = bool
  default     = true
}
