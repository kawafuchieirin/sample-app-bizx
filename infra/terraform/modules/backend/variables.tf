variable "project" {
  type    = string
  default = "bizx"
}

variable "environment" {
  type = string
}

variable "image_tag" {
  description = "ECR image tag deployed to Lambda. CI pushes this before apply."
  type        = string
  default     = "latest"
}

variable "table_name" {
  type = string
}

variable "table_arn" {
  type = string
}

variable "cognito_user_pool_id" {
  type = string
}

variable "cognito_client_id" {
  type = string
}

variable "cors_origins" {
  description = "Comma-separated allowed CORS origins for the API."
  type        = string
}

variable "memory_size" {
  type    = number
  default = 512
}

variable "timeout" {
  type    = number
  default = 15
}
