variable "project" {
  type    = string
  default = "bizx"
}

variable "environment" {
  type = string
}

variable "github_owner" {
  description = "GitHub org/user that owns the repo."
  type        = string
}

variable "github_repo" {
  description = "Repository name."
  type        = string
}

variable "branch" {
  description = "Branch allowed to assume the deploy role."
  type        = string
  default     = "main"
}

variable "create_oidc_provider" {
  description = "Create the GitHub OIDC provider. Set false if it already exists in the account."
  type        = bool
  default     = true
}

variable "ecr_repository_arn" {
  type = string
}

variable "lambda_function_arn" {
  type = string
}

variable "s3_bucket_arn" {
  type = string
}

variable "cloudfront_distribution_arn" {
  type = string
}
