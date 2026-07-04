terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # NOTE: local state for now. Remote state (S3 + DynamoDB lock) is set up in
  # the `bootstrap` config as part of M3.
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "bizx"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
