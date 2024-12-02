terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket         = "sibel-tucana-dev-tf-bucket"
    key            = "terraform/dev/core/terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "sibel-tucana-dev-tf-state-lock"
  }
}

provider "aws" {
  region = "us-east-2"
  allowed_account_ids = [
    "104472814609"
  ]
  default_tags {
    tags = {
      env        = "dev"
      project    = "tucana"
      compliance = "hipaa"
      managed_by = "terraform"
    }
  }
}

module "core" {
  source = "../../modules/core"
  env    = "dev"
}

module "k8s" {
  source       = "../../modules/k8s"
  env          = "dev"
  project_name = "tucana"

  aws_ami_id           = "ami-0b61425d47a44fc5f" # ubuntu 22.04
  aws_kube_master_num  = 1
  aws_kube_worker_num  = 3
  aws_kube_worker_size = "c5.xlarge"

  encryption_key_arn = module.core.encryption_key_arn
}
