variable "project" {
  description = "Project name prefix for resources."
  type        = string
  default     = "bizx"
}

variable "environment" {
  description = "Deployment environment (dev, prod, ...)."
  type        = string
}

variable "domain_prefix" {
  description = "Globally-unique Cognito Hosted UI domain prefix."
  type        = string
}

variable "callback_urls" {
  description = "Allowed OAuth callback URLs (Hosted UI redirects back here)."
  type        = list(string)
  default     = ["http://localhost:5173/"]
}

variable "logout_urls" {
  description = "Allowed sign-out redirect URLs."
  type        = list(string)
  default     = ["http://localhost:5173/"]
}
