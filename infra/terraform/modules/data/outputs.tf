output "table_name" {
  description = "DynamoDB table name (set as BIZX_TABLE_NAME)."
  value       = aws_dynamodb_table.tasks.name
}

output "table_arn" {
  description = "DynamoDB table ARN (for IAM policies)."
  value       = aws_dynamodb_table.tasks.arn
}
