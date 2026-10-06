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
