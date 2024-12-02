output "bastion_ip" {
  value = join("\n", aws_instance.bastion-server.*.public_ip)
}

output "masters" {
  value = join("\n", aws_instance.k8s-master.*.private_ip)
}

output "workers" {
  value = join("\n", aws_instance.k8s-worker.*.private_ip)
}

output "etcd" {
  value = join("\n", ((var.aws_etcd_num > 0) ? (aws_instance.k8s-etcd.*.private_ip) : (aws_instance.k8s-master.*.private_ip)))
}

output "aws_nlb_api_fqdn" {
  value = "${module.aws-nlb.aws_nlb_api_fqdn}:${var.aws_nlb_api_port}"
}

output "inventory" {
  value = data.template_file.inventory.rendered
}

output "private_ssh_key" {
  value = tls_private_key.ssh.private_key_pem
}

output "public_ssh_key" {
  value = tls_private_key.ssh.public_key_openssh
}