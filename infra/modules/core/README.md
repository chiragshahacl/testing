## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 4.16 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | ~> 4.16 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_audit_trail"></a> [audit\_trail](#module\_audit\_trail) | ./modules/ecr_repo | n/a |
| <a name="module_authentication_repository"></a> [authentication\_repository](#module\_authentication\_repository) | ./modules/ecr_repo | n/a |
| <a name="module_central_monitoring_repository"></a> [central\_monitoring\_repository](#module\_central\_monitoring\_repository) | ./modules/ecr_repo | n/a |
| <a name="module_data-stream"></a> [data-stream](#module\_data-stream) | ./modules/ecr_repo | n/a |
| <a name="module_device_repository"></a> [device\_repository](#module\_device\_repository) | ./modules/ecr_repo | n/a |
| <a name="module_emulator"></a> [emulator](#module\_emulator) | ./modules/ecr_repo | n/a |
| <a name="module_hl7_repository"></a> [hl7\_repository](#module\_hl7\_repository) | ./modules/ecr_repo | n/a |
| <a name="module_mirth_repository"></a> [mirth\_repository](#module\_mirth\_repository) | ./modules/ecr_repo | n/a |
| <a name="module_patient_repository"></a> [patient\_repository](#module\_patient\_repository) | ./modules/ecr_repo | n/a |
| <a name="module_realtime_repository"></a> [realtime\_repository](#module\_realtime\_repository) | ./modules/ecr_repo | n/a |
| <a name="module_sdc_repository"></a> [sdc\_repository](#module\_sdc\_repository) | ./modules/ecr_repo | n/a |
| <a name="module_web_repository"></a> [web\_repository](#module\_web\_repository) | ./modules/ecr_repo | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_iam_group.hospitals](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_group) | resource |
| [aws_iam_group_membership.hospitals](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_group_membership) | resource |
| [aws_iam_group_policy.hospital_vitals_put](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_group_policy) | resource |
| [aws_iam_user.hospitals](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user) | resource |
| [aws_kms_key.core_encryption_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key) | resource |
| [aws_route53_zone.dev](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route53_zone) | resource |
| [aws_s3_bucket.vitals](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [aws_s3_bucket_lifecycle_configuration.vitals](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_lifecycle_configuration) | resource |
| [aws_s3_bucket_logging.vitals](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_logging) | resource |
| [aws_s3_bucket_public_access_block.vitals](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block) | resource |
| [aws_s3_bucket_server_side_encryption_configuration.vitals](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_server_side_encryption_configuration) | resource |
| [aws_s3_bucket_versioning.vitals](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_versioning) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_env"></a> [env](#input\_env) | Environment name | `string` | n/a | yes |
| <a name="input_vitals_bucket_users"></a> [vitals\_bucket\_users](#input\_vitals\_bucket\_users) | Usernames with permissions to PUT vitals | `list(string)` | <pre>[<br>  "hospital01",<br>  "hospital02"<br>]</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_dns_zone_name_servers"></a> [dns\_zone\_name\_servers](#output\_dns\_zone\_name\_servers) | The nameservers of the dns zone. |
| <a name="output_encryption_key_arn"></a> [encryption\_key\_arn](#output\_encryption\_key\_arn) | n/a |
| <a name="output_encryption_key_id"></a> [encryption\_key\_id](#output\_encryption\_key\_id) | n/a |
