output "function_name" {
  value = aws_lambda_function.cover_art.function_name
}

output "covers_bucket" {
  value = aws_s3_bucket.covers.bucket
}

output "cover_base_url" {
  description = "Put this in .env as COVER_BASE_URL."
  value       = "https://${aws_cloudfront_distribution.covers.domain_name}"
}
