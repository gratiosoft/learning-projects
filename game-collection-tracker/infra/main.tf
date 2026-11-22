data "aws_caller_identity" "current" {}

locals {
  function_name           = "${var.name}-cover-art"
  scheduled_function_name = "${var.name}-scheduled-backfill"
  ssm_prefix              = "/${var.name}"
  # Bucket names are global; the account id keeps ours unique without a random suffix.
  bucket_name = "${var.name}-covers-${data.aws_caller_identity.current.account_id}"
}

# ---------- S3: private bucket for cover art ----------

resource "aws_s3_bucket" "covers" {
  bucket = local.bucket_name
}

resource "aws_s3_bucket_public_access_block" "covers" {
  bucket                  = aws_s3_bucket.covers.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "covers" {
  bucket = aws_s3_bucket.covers.id
  rule {
    object_ownership = "BucketOwnerEnforced" # disables ACLs
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "covers" {
  bucket = aws_s3_bucket.covers.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Covers are small and replaced in place, so no expiry; just clean up failed uploads.
resource "aws_s3_bucket_lifecycle_configuration" "covers" {
  bucket = aws_s3_bucket.covers.id
  rule {
    id     = "abort-incomplete-uploads"
    status = "Enabled"
    filter {}
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# ---------- CloudFront + Origin Access Control (ADR 0004) ----------

resource "aws_cloudfront_origin_access_control" "covers" {
  name                              = "${var.name}-covers"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "covers" {
  enabled         = true
  comment         = "Game cover art"
  price_class     = "PriceClass_100"
  is_ipv6_enabled = true

  origin {
    domain_name              = aws_s3_bucket.covers.bucket_regional_domain_name
    origin_id                = "covers"
    origin_access_control_id = aws_cloudfront_origin_access_control.covers.id
  }

  default_cache_behavior {
    target_origin_id       = "covers"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true
    # AWS managed policy "CachingOptimized".
    cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# Only this distribution may read objects. The bucket itself stays non-public.
data "aws_iam_policy_document" "bucket" {
  statement {
    sid       = "AllowCloudFrontRead"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.covers.arn}/covers/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.covers.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "covers" {
  bucket = aws_s3_bucket.covers.id
  policy = data.aws_iam_policy_document.bucket.json

  depends_on = [aws_s3_bucket_public_access_block.covers]
}

# ---------- Secrets (values are set outside Terraform) ----------

# Terraform creates the parameters with a placeholder and then ignores the value,
# so real secrets never enter state. Set them with:
#   aws ssm put-parameter --name /game-tracker/RAWG_API_KEY --type SecureString --overwrite --value ...
resource "aws_ssm_parameter" "secret" {
  for_each = toset(["AIRTABLE_TOKEN", "RAWG_API_KEY"])

  name  = "${local.ssm_prefix}/${each.key}"
  type  = "SecureString"
  value = "CHANGE_ME"

  lifecycle {
    ignore_changes = [value]
  }
}

# ---------- Lambda ----------

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.function_name}"
  retention_in_days = 14
}

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${local.function_name}-role"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

data "aws_iam_policy_document" "lambda" {
  statement {
    sid       = "WriteCovers"
    actions   = ["s3:PutObject", "s3:GetObject"]
    resources = ["${aws_s3_bucket.covers.arn}/covers/*"]
  }

  # Without s3:ListBucket, HeadObject on a missing key returns 403 instead of 404,
  # which would break the handler's "does the cover exist?" check.
  statement {
    sid       = "ExistenceCheck"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.covers.arn]
  }

  statement {
    sid     = "ReadSecrets"
    actions = ["ssm:GetParameter"]
    resources = [
      for p in aws_ssm_parameter.secret : p.arn
    ]
  }

  statement {
    sid     = "Logs"
    actions = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = [
      "${aws_cloudwatch_log_group.lambda.arn}:*",
      "${aws_cloudwatch_log_group.scheduled.arn}:*",
    ]
  }
}

resource "aws_iam_role_policy" "lambda" {
  name   = "least-privilege"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda.json
}

resource "aws_lambda_function" "cover_art" {
  function_name    = local.function_name
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  handler          = "game_tracker.handler.lambda_handler"
  filename         = var.lambda_package
  source_code_hash = filebase64sha256(var.lambda_package)
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      AIRTABLE_BASE_ID = var.airtable_base_id
      AIRTABLE_TABLE   = var.airtable_table
      COVERS_BUCKET    = aws_s3_bucket.covers.bucket
      COVER_BASE_URL   = "https://${aws_cloudfront_distribution.covers.domain_name}"
      SSM_PREFIX       = local.ssm_prefix
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda, aws_iam_role_policy.lambda]
}

# ---------- Scheduled backfill (ADR 0008) ----------
# Same zip, role and environment as cover_art; only the handler, timeout and log group differ.

resource "aws_cloudwatch_log_group" "scheduled" {
  name              = "/aws/lambda/${local.scheduled_function_name}"
  retention_in_days = 14
}

resource "aws_lambda_function" "scheduled_backfill" {
  function_name    = local.scheduled_function_name
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  handler          = "game_tracker.handler.scheduled_backfill"
  filename         = var.lambda_package
  source_code_hash = filebase64sha256(var.lambda_package)
  timeout          = 300
  memory_size      = 256

  environment {
    variables = {
      AIRTABLE_BASE_ID = var.airtable_base_id
      AIRTABLE_TABLE   = var.airtable_table
      COVERS_BUCKET    = aws_s3_bucket.covers.bucket
      COVER_BASE_URL   = "https://${aws_cloudfront_distribution.covers.domain_name}"
      SSM_PREFIX       = local.ssm_prefix
      MAX_PER_RUN      = tostring(var.max_per_run)
    }
  }

  depends_on = [aws_cloudwatch_log_group.scheduled, aws_iam_role_policy.lambda]
}

resource "aws_cloudwatch_event_rule" "backfill" {
  name                = "${local.scheduled_function_name}-schedule"
  description         = "Fills in missing cover art for new games."
  schedule_expression = var.backfill_schedule
  state               = var.backfill_enabled ? "ENABLED" : "DISABLED"
}

resource "aws_cloudwatch_event_target" "backfill" {
  rule = aws_cloudwatch_event_rule.backfill.name
  arn  = aws_lambda_function.scheduled_backfill.arn
}

resource "aws_lambda_permission" "events_invoke_backfill" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scheduled_backfill.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.backfill.arn
}
