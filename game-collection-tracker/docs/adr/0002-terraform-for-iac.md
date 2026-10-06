# 0002. Terraform for infrastructure as code

Status: accepted

## Context
Repo rules allow AWS CDK or Terraform. CDK would pull a Node toolchain into a Python project.

## Decision
Terraform in `infra/`, local state (gitignored) because this is a single-owner learning project. Resources: S3 bucket, CloudFront + OAC, Lambda, IAM role, CloudWatch log group, SSM parameters.

## Consequences
- Declarative and readable; `terraform plan` shows exactly what changes.
- Local state is a single point of failure and must never be committed (it can contain resource details). Moving to an S3 backend is a possible later step, deliberately skipped now to avoid a chicken-and-egg bucket.
- Nothing is applied without explicit owner approval.
