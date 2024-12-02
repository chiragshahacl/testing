output "dns_zone_name_servers" {
  description = "The nameservers of the dns zone."
  value       = aws_route53_zone.monitoring.name_servers
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.monitoring-non-prod-eks.cluster_name
}