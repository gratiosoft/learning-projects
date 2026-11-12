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
