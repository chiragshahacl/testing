variable "env" {
  description = "Environment name"
  type        = string
  nullable    = false
}

variable "vitals_bucket_users" {
  description = "Usernames with permissions to PUT vitals"
  type        = list(string)
  default     = ["vitals-uploader"]
}