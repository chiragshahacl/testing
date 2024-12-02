resource "aws_kms_key" "core_encryption_key" {
  description             = "core-encryption-key"
  key_usage               = "ENCRYPT_DECRYPT"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}