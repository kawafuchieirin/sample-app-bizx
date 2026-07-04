output "deploy_role_arn" {
  description = "IAM role ARN for GitHub Actions to assume (set as secret AWS_DEPLOY_ROLE_ARN)."
  value       = aws_iam_role.deploy.arn
}
