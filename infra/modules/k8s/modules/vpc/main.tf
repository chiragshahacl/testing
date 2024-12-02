resource "aws_vpc" "cluster-vpc" {
  cidr_block = var.aws_vpc_cidr_block

  #DNS Related Entries
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    name = "kubernetes-${var.aws_cluster_name}-vpc"
  }

}

resource "aws_eip" "cluster-nat-eip" {
  count = length(var.aws_cidr_subnets_public)
  vpc   = true
}

resource "aws_internet_gateway" "cluster-vpc-internetgw" {
  vpc_id = aws_vpc.cluster-vpc.id

  tags = {
    name = "kubernetes-${var.aws_cluster_name}-internetgw"
  }

}

resource "aws_subnet" "cluster-vpc-subnets-public" {
  vpc_id            = aws_vpc.cluster-vpc.id
  count             = length(var.aws_cidr_subnets_public)
  availability_zone = element(var.aws_avail_zones, count.index % length(var.aws_avail_zones))
  cidr_block        = element(var.aws_cidr_subnets_public, count.index)

  tags = {
    name                                            = "kubernetes-${var.aws_cluster_name}-${element(var.aws_avail_zones, count.index)}-public"
    "kubernetes.io/cluster/${var.aws_cluster_name}" = "shared"
    "kubernetes.io/role/elb"                        = "1"
  }

}

resource "aws_nat_gateway" "cluster-nat-gateway" {
  count         = length(var.aws_cidr_subnets_public)
  allocation_id = element(aws_eip.cluster-nat-eip.*.id, count.index)
  subnet_id     = element(aws_subnet.cluster-vpc-subnets-public.*.id, count.index)
}

resource "aws_subnet" "cluster-vpc-subnets-private" {
  vpc_id            = aws_vpc.cluster-vpc.id
  count             = length(var.aws_cidr_subnets_private)
  availability_zone = element(var.aws_avail_zones, count.index % length(var.aws_avail_zones))
  cidr_block        = element(var.aws_cidr_subnets_private, count.index)

  tags = {
    name                                            = "kubernetes-${var.aws_cluster_name}-${element(var.aws_avail_zones, count.index)}-private"
    "kubernetes.io/cluster/${var.aws_cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"               = "1"
  }

}

#Routing in VPC

resource "aws_route_table" "kubernetes-public" {
  vpc_id = aws_vpc.cluster-vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.cluster-vpc-internetgw.id
  }

  tags = {
    name = "kubernetes-${var.aws_cluster_name}-routetable-public"
  }

}

resource "aws_route_table" "kubernetes-private" {
  count  = length(var.aws_cidr_subnets_private)
  vpc_id = aws_vpc.cluster-vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = element(aws_nat_gateway.cluster-nat-gateway.*.id, count.index)
  }

  tags = {
    name = "kubernetes-${var.aws_cluster_name}-routetable-private-${count.index}"
  }
}

resource "aws_route_table_association" "kubernetes-public" {
  count          = length(var.aws_cidr_subnets_public)
  subnet_id      = element(aws_subnet.cluster-vpc-subnets-public.*.id, count.index)
  route_table_id = aws_route_table.kubernetes-public.id
}

resource "aws_route_table_association" "kubernetes-private" {
  count          = length(var.aws_cidr_subnets_private)
  subnet_id      = element(aws_subnet.cluster-vpc-subnets-private.*.id, count.index)
  route_table_id = element(aws_route_table.kubernetes-private.*.id, count.index)
}

#Kubernetes Security Groups

resource "aws_security_group" "kubernetes" {
  name        = "kubernetes-${var.aws_cluster_name}-securitygroup"
  description = "Kubernetes Security Groups"

  vpc_id = aws_vpc.cluster-vpc.id

  tags = {
    name = "kubernetes-${var.aws_cluster_name}-securitygroup"
  }
}

resource "aws_security_group_rule" "allow-all-ingress" {
  description = "allow ingress from VPC"

  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = [var.aws_vpc_cidr_block]
  security_group_id = aws_security_group.kubernetes.id
}

resource "aws_security_group_rule" "allow-all-egress" {
  description = "allow all egress"

  type      = "egress"
  from_port = 0
  to_port   = 65535
  protocol  = "-1"
  #tfsec:ignore:aws-ec2-no-public-egress-sgr
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.kubernetes.id
}

resource "aws_security_group_rule" "allow-ssh-connections" {
  description = "allow ssh for cluster administration"

  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "TCP"
  cidr_blocks       = var.allow_ssh_connections_cidr
  security_group_id = aws_security_group.kubernetes.id
}

resource "aws_security_group_rule" "allow-http-connections" {
  description = "allow HTTP inbound"

  type      = "ingress"
  from_port = 80
  to_port   = 80
  protocol  = "TCP"
  #tfsec:ignore:aws-ec2-no-public-ingress-sgr
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.kubernetes.id
}

resource "aws_security_group_rule" "allow-https-connections" {
  description = "allow HTTPS inbound"

  type      = "ingress"
  from_port = 443
  to_port   = 443
  protocol  = "TCP"
  #tfsec:ignore:aws-ec2-no-public-ingress-sgr
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.kubernetes.id
}

resource "aws_security_group_rule" "allow-tcp-6661-connections" {
  description = "allow TCP inbound for Mirth"

  type      = "ingress"
  from_port = 6661
  to_port   = 6661
  protocol  = "TCP"
  #tfsec:ignore:aws-ec2-no-public-ingress-sgr
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.kubernetes.id
}

#VPC flow logs
resource "aws_s3_bucket" "cluster-vpc-flow-logs" {
  bucket = "kubernetes-${var.aws_cluster_name}-vpc-flow-logs"
}

resource "aws_s3_bucket_logging" "cluster-vpc-flow-logs" {
  bucket = aws_s3_bucket.cluster-vpc-flow-logs.id

  target_bucket = aws_s3_bucket.cluster-vpc-flow-logs.id
  target_prefix = "log/"
}

resource "aws_s3_bucket_public_access_block" "cluster-vpc-flow-logs" {
  bucket = aws_s3_bucket.cluster-vpc-flow-logs.id

  restrict_public_buckets = true
  block_public_policy     = true
  block_public_acls       = true
  ignore_public_acls      = true
}

resource "aws_s3_bucket_versioning" "cluster-vpc-flow-logs" {
  bucket = aws_s3_bucket.cluster-vpc-flow-logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cluster-vpc-flow-logs" {
  bucket = aws_s3_bucket.cluster-vpc-flow-logs.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = var.encryption_key_arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_flow_log" "cluster-vpc" {
  log_destination      = aws_s3_bucket.cluster-vpc-flow-logs.arn
  log_destination_type = "s3"
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.cluster-vpc.id
}

resource "aws_s3_bucket_ownership_controls" "cluster-vpc" {
  bucket = aws_s3_bucket.cluster-vpc-flow-logs.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "cluster-vpc" {
  depends_on = [aws_s3_bucket_ownership_controls.cluster-vpc]

  bucket = aws_s3_bucket.cluster-vpc-flow-logs.id
  acl    = "log-delivery-write"
}