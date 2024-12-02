output "encryption_key_id" {
  value = aws_kms_key.core_encryption_key.id
}

output "encryption_key_arn" {
  value = aws_kms_key.core_encryption_key.arn
}

output "dns_zone_name_servers" {
  description = "The nameservers of the dns zone."
  value       = aws_route53_zone.dev.name_servers
}