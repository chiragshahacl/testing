locals {

  aws_cluster_name = "${var.project_name}-${var.env}"

}

data "aws_availability_zones" "available" {}

/*
* Calling modules who create the initial AWS VPC / AWS ELB
* for Kubernetes Deployment
*/

module "aws-vpc" {
  source = "./modules/vpc"

  aws_cluster_name           = local.aws_cluster_name
  aws_vpc_cidr_block         = var.aws_vpc_cidr_block
  aws_avail_zones            = data.aws_availability_zones.available.names
  aws_cidr_subnets_private   = var.aws_cidr_subnets_private
  aws_cidr_subnets_public    = var.aws_cidr_subnets_public
  allow_ssh_connections_cidr = var.allow_ssh_connections_cidr

  encryption_key_arn = var.encryption_key_arn
}

module "aws-nlb" {
  source = "./modules/nlb"

  aws_cluster_name       = local.aws_cluster_name
  aws_vpc_id             = module.aws-vpc.aws_vpc_id
  aws_avail_zones        = data.aws_availability_zones.available.names
  aws_subnet_ids_public  = module.aws-vpc.aws_subnet_ids_public
  aws_subnet_ids_private = module.aws-vpc.aws_subnet_ids_private
  aws_nlb_api_port       = var.aws_nlb_api_port
  k8s_secure_api_port    = var.k8s_secure_api_port
}

module "aws-iam" {
  source = "./modules/iam"

  aws_cluster_name = local.aws_cluster_name
}


/*
* Create SSH key pair
*
*/

resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "ssh" {
  key_name   = var.ssh_key_name
  public_key = tls_private_key.ssh.public_key_openssh
}

/*
* Create Bastion Instances in AWS
*
*/

resource "aws_instance" "bastion-server" {
  count                       = var.aws_bastion_num
  ami                         = var.aws_ami_id
  instance_type               = var.aws_bastion_size
  monitoring                  = true
  associate_public_ip_address = true
  subnet_id                   = element(module.aws-vpc.aws_subnet_ids_public, count.index)
  vpc_security_group_ids      = module.aws-vpc.aws_security_group
  key_name                    = aws_key_pair.ssh.key_name

  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
  }

  iam_instance_profile = module.aws-iam.kube-worker-profile

  root_block_device {
    encrypted = true
  }

  tags = {
    name    = "kubernetes-${local.aws_cluster_name}-bastion-${count.index}"
    cluster = local.aws_cluster_name
    role    = "bastion-${local.aws_cluster_name}-${count.index}"
  }

}

/*
* Create K8s Master and worker nodes and etcd instances
*
*/

resource "aws_instance" "k8s-master" {
  count                  = var.aws_kube_master_num
  ami                    = var.aws_ami_id
  instance_type          = var.aws_kube_master_size
  monitoring             = true
  subnet_id              = element(module.aws-vpc.aws_subnet_ids_private, count.index)
  vpc_security_group_ids = module.aws-vpc.aws_security_group
  key_name               = aws_key_pair.ssh.key_name

  root_block_device {
    volume_size = var.aws_kube_master_disk_size
    encrypted   = true
  }


  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
  }

  iam_instance_profile = module.aws-iam.kube_control_plane-profile

  tags = {
    name                                              = "kubernetes-${local.aws_cluster_name}-master${count.index}"
    "kubernetes.io/cluster/${local.aws_cluster_name}" = "member"
    role                                              = "master"
  }

}

resource "aws_lb_target_group_attachment" "tg-attach_master_nodes" {
  count            = var.aws_kube_master_num
  target_group_arn = module.aws-nlb.aws_nlb_api_tg_arn
  target_id        = element(aws_instance.k8s-master.*.private_ip, count.index)
}

resource "aws_instance" "k8s-etcd" {
  count                  = var.aws_etcd_num
  ami                    = var.aws_ami_id
  instance_type          = var.aws_etcd_size
  monitoring             = true
  subnet_id              = element(module.aws-vpc.aws_subnet_ids_private, count.index)
  vpc_security_group_ids = module.aws-vpc.aws_security_group
  key_name               = aws_key_pair.ssh.key_name

  root_block_device {
    volume_size = var.aws_etcd_disk_size
    encrypted   = true
  }

  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
  }

  tags = {
    name                                              = "kubernetes-${local.aws_cluster_name}-etcd${count.index}"
    "kubernetes.io/cluster/${local.aws_cluster_name}" = "member"
    role                                              = "etcd"
  }

}

resource "aws_instance" "k8s-worker" {
  count                  = var.aws_kube_worker_num
  ami                    = var.aws_ami_id
  instance_type          = var.aws_kube_worker_size
  monitoring             = true
  subnet_id              = element(module.aws-vpc.aws_subnet_ids_private, count.index)
  vpc_security_group_ids = module.aws-vpc.aws_security_group
  key_name               = aws_key_pair.ssh.key_name

  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
  }

  iam_instance_profile = module.aws-iam.kube-worker-profile

  root_block_device {
    volume_size = var.aws_kube_worker_disk_size
    encrypted   = true
  }

  ebs_block_device {
    device_name           = "/dev/sdf"
    volume_type           = "gp3"
    volume_size           = var.aws_kube_worker_data_disk_size
    delete_on_termination = false
    encrypted             = true
  }

  tags = {
    name                                              = "kubernetes-${local.aws_cluster_name}-worker${count.index}"
    "kubernetes.io/cluster/${local.aws_cluster_name}" = "member"
    role                                              = "worker"
  }

}

/*
* Create Kubespray Inventory File
*
*/
data "template_file" "inventory" {
  template = file("${path.module}/templates/inventory.tpl")

  vars = {
    public_ip_address_bastion = join("\n", formatlist("bastion ansible_host=%s", aws_instance.bastion-server.*.public_ip))
    connection_strings_master = join("\n", formatlist("%s ansible_host=%s", aws_instance.k8s-master.*.private_dns, aws_instance.k8s-master.*.private_ip))
    connection_strings_node   = join("\n", formatlist("%s ansible_host=%s", aws_instance.k8s-worker.*.private_dns, aws_instance.k8s-worker.*.private_ip))
    list_master               = join("\n", aws_instance.k8s-master.*.private_dns)
    list_node                 = join("\n", aws_instance.k8s-worker.*.private_dns)
    connection_strings_etcd   = join("\n", formatlist("%s ansible_host=%s", aws_instance.k8s-etcd.*.private_dns, aws_instance.k8s-etcd.*.private_ip))
    list_etcd                 = join("\n", ((var.aws_etcd_num > 0) ? (aws_instance.k8s-etcd.*.private_dns) : (aws_instance.k8s-master.*.private_dns)))
    nlb_api_fqdn              = "apiserver_loadbalancer_domain_name=\"${module.aws-nlb.aws_nlb_api_fqdn}\""
  }
}

resource "null_resource" "inventories" {
  provisioner "local-exec" {
    command = "echo '${data.template_file.inventory.rendered}' > ${var.inventory_file}"
  }

  triggers = {
    template = data.template_file.inventory.rendered
  }
}
