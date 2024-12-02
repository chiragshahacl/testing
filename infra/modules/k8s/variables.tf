variable "ssh_key_name" {
  description = "Name of the SSH keypair to use in AWS."
  default     = "tucana"
}

variable "encryption_key_arn" {
  description = "AWS encryption key arn"
}

//General Cluster Settings

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

variable "aws_ami_id" {
  description = "debian-10 ami ID"
  default     = "ami-06d899edde08824a3"
}

# data "aws_ami" "distro" {
#   most_recent = true

#   filter {
#     name   = "name"
#     values = ["debian-10-amd64-*"]
#   }

#   filter {
#     name   = "virtualization-type"
#     values = ["hvm"]
#   }

#   owners = ["136693071363"] # Debian-10
# }

//AWS VPC Variables

variable "aws_vpc_cidr_block" {
  description = "CIDR Block for VPC"
  default     = "10.250.192.0/18"
}

variable "aws_cidr_subnets_private" {
  description = "CIDR Blocks for private subnets in Availability Zones"
  type        = list(string)
  default     = ["10.250.192.0/20"]
}

variable "aws_cidr_subnets_public" {
  description = "CIDR Blocks for public subnets in Availability Zones"
  type        = list(string)
  default     = ["10.250.224.0/20"]
}

//AWS EC2 Settings

variable "aws_bastion_size" {
  description = "EC2 Instance Size of Bastion Host"
  default     = "t3.small"
}

variable "aws_bastion_num" {
  description = "Number of Bastion Nodes"
  default     = 1
}

variable "aws_kube_master_num" {
  description = "Number of Kubernetes Master Nodes"
  default     = 3
}

variable "aws_kube_master_disk_size" {
  description = "Disk size for Kubernetes Master Nodes (in GiB)"
  default     = 50
}

variable "aws_kube_master_size" {
  description = "Instance size of Kube Master Nodes"
  default     = "t3.medium"
}

variable "aws_etcd_num" {
  description = "Number of etcd Nodes"
  default     = 0
}

variable "aws_etcd_disk_size" {
  description = "Disk size for etcd Nodes (in GiB)"
  default     = 50
}

variable "aws_etcd_size" {
  description = "Instance size of etcd Nodes"
  default     = "t3.medium"
}

variable "aws_kube_worker_num" {
  description = "Number of Kubernetes Worker Nodes"
  default     = 5
}

variable "aws_kube_worker_disk_size" {
  description = "Disk size for Kubernetes Worker Nodes (in GiB)"
  default     = 50
}

variable "aws_kube_worker_data_disk_size" {
  description = "Additional Disk size for Kubernetes Worker Nodes (in GiB)"
  default     = 100
}

variable "aws_kube_worker_size" {
  description = "Instance size of Kubernetes Worker Nodes"
  default     = "t3.medium"
}

/*
* AWS NLB Settings
*
*/
variable "aws_nlb_api_port" {
  description = "Port for AWS NLB"
  default     = 6443
}

variable "k8s_secure_api_port" {
  description = "Secure Port of K8S API Server"
  default     = 6443
}

variable "inventory_file" {
  description = "Where to store the generated inventory file"
  default     = "hosts"
}


variable "allow_ssh_connections_cidr" {
  description = "CIDR Blocks for public subnets in Availability zones"
  type        = list(string)
  #  default     =  ["0.0.0.0/0"]
  default = ["130.41.32.87/32"]
}


