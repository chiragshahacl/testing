terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket         = "sibel-tucana-monitoring-tf-bucket"
    key            = "terraform/monitoring/non-prod/terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "sibel-tucana-monitoring-non-prod-tf-state-lock"
  }
}

provider "aws" {
  region = "us-east-2"
  allowed_account_ids = [
    "630003401982"
  ]
  default_tags {
    tags = {
      env        = "monitoring-non-prod"
      project    = "tucana"
      compliance = "hipaa"
      managed_by = "terraform"
    }
  }
}

resource "aws_kms_key" "core_encryption_key" {
  description             = "core-encryption-key"
  key_usage               = "ENCRYPT_DECRYPT"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_route53_zone" "monitoring" {
  name = "mon.tucana.sibel.health"
}

module "monitoring-non-prod-eks" {
  source       = "../../../modules/eks"
  env          = "monitoring-non-prod"
  project_name = "tucana"

  encryption_key_arn = aws_kms_key.core_encryption_key.arn

  node_instance_types = ["t3.xlarge"]
}