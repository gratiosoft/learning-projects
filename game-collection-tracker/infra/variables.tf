variable "region" {
  description = "AWS region for all resources."
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Named AWS CLI profile to use. Null uses the default credential chain."
  type        = string
  default     = null
}

variable "airtable_base_id" {
  description = "Airtable base ID (app...). Not a secret."
  type        = string

  # Fails `terraform plan` on a malformed ID (e.g. a stray "# comment" copied from .env)
  # instead of shipping it to the Lambda.
  validation {
    condition     = can(regex("^app[A-Za-z0-9]{14}$", var.airtable_base_id))
    error_message = "airtable_base_id must be 'app' followed by 14 letters/digits."
  }
}

variable "airtable_table" {
  description = "Airtable table name."
  type        = string
  default     = "Games"
}

variable "name" {
  description = "Prefix for resource names."
  type        = string
  default     = "game-tracker"
}

variable "lambda_package" {
  description = "Path to the zip built by `make package`."
  type        = string
  default     = "../build/lambda.zip"
}

variable "backfill_schedule" {
  description = "EventBridge schedule for the cover backfill: rate(...) or cron(...)."
  type        = string
  default     = "rate(1 day)"

  validation {
    condition = can(regex("^(rate\\([0-9]+ (minute|minutes|hour|hours|day|days)\\)|cron\\(.+\\))$",
    var.backfill_schedule))
    error_message = "backfill_schedule must look like 'rate(1 day)' or 'cron(0 6 * * ? *)'."
  }
}

variable "backfill_enabled" {
  description = "Set to false to switch the scheduled backfill off without destroying it."
  type        = bool
  default     = true
}

variable "max_per_run" {
  description = "Most games the scheduled backfill processes per run."
  type        = number
  default     = 10

  validation {
    condition     = var.max_per_run >= 1 && var.max_per_run <= 50
    error_message = "max_per_run must be between 1 and 50."
  }
}
