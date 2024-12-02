output "bastion_ip" {
  value = module.k8s.bastion_ip
}

output "inventory" {
  value = module.k8s.inventory
}

output "public_ssh_key" {
  value = module.k8s.public_ssh_key
}

output "private_ssh_key" {
  value     = module.k8s.private_ssh_key
  sensitive = true
}

output "dns_zone_name_servers" {
  value = module.core.dns_zone_name_servers
}