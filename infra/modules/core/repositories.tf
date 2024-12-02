# PLATFORM REPOSITORIES

module "authentication_repository" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "authentication"
}

module "device_repository" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "device"
}

module "patient_repository" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "patient"
}

module "config_repository" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "config"
}

module "auth_repository" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "auth"
}

module "audit_trail" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "audit-trail"
}

module "emulator" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "emulator"
}

module "data-stream" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "data-stream"
}

module "rkc" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "rkc"
}

# GATEWAY REPOSITORIES

module "hl7_repository" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "hl7"
}

module "realtime_repository" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "realtime"
}

module "sdc_repository" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "sdc"
}

module "web_repository" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "web"
}

module "mirth_repository" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "mirth"
}

# Cron repositories
module "upload_vitals_repository" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "upload-vitals"
}

# Sites Repositories

module "central_monitoring_repository" {
  source            = "./modules/ecr_repo"
  encryption_key_id = aws_kms_key.core_encryption_key.id
  repository_name   = "central-monitoring"
}

