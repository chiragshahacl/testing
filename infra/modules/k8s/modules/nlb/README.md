## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_lb.aws-nlb-api](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb) | resource |
| [aws_lb_listener.aws-nlb-api-listener](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_listener) | resource |
| [aws_lb_target_group.aws-nlb-api-tg](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_target_group) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_aws_avail_zones"></a> [aws\_avail\_zones](#input\_aws\_avail\_zones) | Availability Zones Used | `list(string)` | n/a | yes |
| <a name="input_aws_cluster_name"></a> [aws\_cluster\_name](#input\_aws\_cluster\_name) | Name of Cluster | `any` | n/a | yes |
| <a name="input_aws_nlb_api_port"></a> [aws\_nlb\_api\_port](#input\_aws\_nlb\_api\_port) | Port for AWS NLB | `any` | n/a | yes |
| <a name="input_aws_nlb_internal"></a> [aws\_nlb\_internal](#input\_aws\_nlb\_internal) | Port for AWS NLB | `bool` | `true` | no |
| <a name="input_aws_subnet_ids_private"></a> [aws\_subnet\_ids\_private](#input\_aws\_subnet\_ids\_private) | IDs of Private Subnets | `list(string)` | n/a | yes |
| <a name="input_aws_subnet_ids_public"></a> [aws\_subnet\_ids\_public](#input\_aws\_subnet\_ids\_public) | IDs of Public Subnets | `list(string)` | n/a | yes |
| <a name="input_aws_vpc_id"></a> [aws\_vpc\_id](#input\_aws\_vpc\_id) | AWS VPC ID | `any` | n/a | yes |
| <a name="input_k8s_secure_api_port"></a> [k8s\_secure\_api\_port](#input\_k8s\_secure\_api\_port) | Secure Port of K8S API Server | `any` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_aws_nlb_api_fqdn"></a> [aws\_nlb\_api\_fqdn](#output\_aws\_nlb\_api\_fqdn) | n/a |
| <a name="output_aws_nlb_api_id"></a> [aws\_nlb\_api\_id](#output\_aws\_nlb\_api\_id) | n/a |
| <a name="output_aws_nlb_api_tg_arn"></a> [aws\_nlb\_api\_tg\_arn](#output\_aws\_nlb\_api\_tg\_arn) | n/a |
