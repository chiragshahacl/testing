variable "repository_name" {
  description = "Name of the ECR repository"
  type        = string
  nullable    = false
}


variable "encryption_key_id" {
  description = "ID of the KMS key to use"
  type        = string
  nullable    = false
}