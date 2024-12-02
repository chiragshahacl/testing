variable "env" {
  description = "Environment name"
  type        = string
  nullable    = false
}

variable "project_name" {
  description = "Project name"
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^([a-z]+-)*([a-z]+)$", var.project_name))
    error_message = "The project name must be words (only letters), lowercase, and separated by hyphens"
  }
}

variable "kubernetes_version" {
  description = "Name to be used on all the resources as identifier"
  type        = string
  default     = "1.26"
}

variable "encryption_key_arn" {
  description = "AWS encryption key arn"
}

# VPC vars
variable "aws_vpc_cidr_block" {
  description = "CIDR Block for VPC"
  default     = "10.250.192.0/18"
}

variable "aws_cidr_subnets_private" {
  description = "CIDR Blocks for private subnets in Availability Zones"
  type        = list(string)
  default     = ["10.250.192.0/20", "10.250.208.0/20"]
}

variable "aws_cidr_subnets_public" {
  description = "CIDR Blocks for public subnets in Availability Zones"
  type        = list(string)
  default     = ["10.250.224.0/20", "10.250.240.0/20"]
}

# Node group vars
variable "node_disk_size" {
  description = "Disk size in GiB for worker nodes"
  type        = number
  default     = 50
}

variable "node_instance_types" {
  description = "List of instance types associated with the EKS Node Group"
  type        = list(string)
  default     = ["t3.medium"]
}