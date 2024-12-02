terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
}

data "aws_kms_key" "core_encryption_key" {
  key_id = var.encryption_key_id
}

# tfsec:ignore:aws-ecr-enforce-immutable-repository
resource "aws_ecr_repository" "project_ecr_repository" {
  name = var.repository_name

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = data.aws_kms_key.core_encryption_key.arn
  }
}

resource "aws_ecr_lifecycle_policy" "project_ecr_repo_lifecycle" {
  policy = jsonencode({
    rules = [
      {
        rulePriority = 10
        description  = "Keep Release images"
        selection = {
          tagStatus   = "tagged"
          tagPrefixList =  ["v"]
          countType   = "imageCountMoreThan"
          countNumber = 99999
        }
        action = {
          type = "expire"
        },
      },
      {
        rulePriority = 20
        description  = "Keep last 10 images for the rest"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        },
      }
    ]
  })


  repository = aws_ecr_repository.project_ecr_repository.name
}
