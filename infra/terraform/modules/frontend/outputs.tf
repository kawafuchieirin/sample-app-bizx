output "bucket_name" {
  description = "S3 bucket that holds the built SPA (CI syncs dist/ here)."
  value       = aws_s3_bucket.site.id
}

output "distribution_id" {
  description = "CloudFront distribution ID (for cache invalidation)."
  value       = aws_cloudfront_distribution.site.id
}

output "distribution_arn" {
  value = aws_cloudfront_distribution.site.arn
}

output "bucket_arn" {
  value = aws_s3_bucket.site.arn
}

output "cloudfront_domain" {
  description = "CloudFront domain name."
  value       = aws_cloudfront_distribution.site.domain_name
}

output "url" {
  description = "Public site URL."
  value       = "https://${aws_cloudfront_distribution.site.domain_name}/"
}
