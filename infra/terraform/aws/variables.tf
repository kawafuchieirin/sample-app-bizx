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

variable "callback_urls" {
  description = "Allowed OAuth callback URLs."
  type        = list(string)
  default     = ["http://localhost:5173/"]
}

variable "logout_urls" {
  description = "Allowed sign-out redirect URLs."
  type        = list(string)
  default     = ["http://localhost:5173/"]
}
