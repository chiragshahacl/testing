terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket         = "sibel-tucana-prod-tf-bucket"
    key            = "terraform/prod/core/terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "sibel-tucana-prod-tf-state-lock"
  }
}

provider "aws" {
  region = "us-east-2"
  allowed_account_ids = [
    "620908046246"
  ]
  default_tags {
    tags = {
      env        = "prod"
      project    = "tucana"
      compliance = "hipaa"
      managed_by = "terraform"
    }
  }
}

module "core" {
  source = "../../modules/core"
  env    = "prod"
}

module "k8s" {
  source       = "../../modules/k8s"
  env          = "prod"
  project_name = "tucana"

  aws_ami_id                     = "ami-0b61425d47a44fc5f" # ubuntu 22.04
  aws_kube_master_num            = 1
  aws_kube_worker_num            = 3
  aws_kube_worker_size           = "c5.xlarge"
  aws_kube_worker_data_disk_size = 500

  encryption_key_arn = module.core.encryption_key_arn
}