output "api_url" {
  description = "Base URL of the HTTP API (append /api/v1)."
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "ecr_repository_url" {
  description = "ECR repository URL to push the Lambda image to."
  value       = aws_ecr_repository.api.repository_url
}

output "ecr_repository_arn" {
  value = aws_ecr_repository.api.arn
}

output "lambda_function_name" {
  description = "Lambda function name (for CI update-function-code)."
  value       = aws_lambda_function.api.function_name
}

output "lambda_function_arn" {
  value = aws_lambda_function.api.arn
}
