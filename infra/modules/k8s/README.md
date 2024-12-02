## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |
| <a name="provider_null"></a> [null](#provider\_null) | n/a |
| <a name="provider_template"></a> [template](#provider\_template) | n/a |
| <a name="provider_tls"></a> [tls](#provider\_tls) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_aws-iam"></a> [aws-iam](#module\_aws-iam) | ./modules/iam | n/a |
| <a name="module_aws-nlb"></a> [aws-nlb](#module\_aws-nlb) | ./modules/nlb | n/a |
| <a name="module_aws-vpc"></a> [aws-vpc](#module\_aws-vpc) | ./modules/vpc | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_instance.bastion-server](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance) | resource |
| [aws_instance.k8s-etcd](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance) | resource |
| [aws_instance.k8s-master](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance) | resource |
| [aws_instance.k8s-worker](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance) | resource |
| [aws_key_pair.ssh](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/key_pair) | resource |
| [aws_lb_target_group_attachment.tg-attach_master_nodes](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_target_group_attachment) | resource |
| [null_resource.inventories](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [tls_private_key.ssh](https://registry.terraform.io/providers/hashicorp/tls/latest/docs/resources/private_key) | resource |
| [aws_availability_zones.available](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/availability_zones) | data source |
| [template_file.inventory](https://registry.terraform.io/providers/hashicorp/template/latest/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_allow_ssh_connections_cidr"></a> [allow\_ssh\_connections\_cidr](#input\_allow\_ssh\_connections\_cidr) | CIDR Blocks for public subnets in Availability zones | `list(string)` | <pre>[<br>  "130.41.32.87/32"<br>]</pre> | no |
| <a name="input_aws_ami_id"></a> [aws\_ami\_id](#input\_aws\_ami\_id) | debian-10 ami ID | `string` | `"ami-06d899edde08824a3"` | no |
| <a name="input_aws_bastion_num"></a> [aws\_bastion\_num](#input\_aws\_bastion\_num) | Number of Bastion Nodes | `number` | `1` | no |
| <a name="input_aws_bastion_size"></a> [aws\_bastion\_size](#input\_aws\_bastion\_size) | EC2 Instance Size of Bastion Host | `string` | `"t3.small"` | no |
| <a name="input_aws_cidr_subnets_private"></a> [aws\_cidr\_subnets\_private](#input\_aws\_cidr\_subnets\_private) | CIDR Blocks for private subnets in Availability Zones | `list(string)` | <pre>[<br>  "10.250.192.0/20"<br>]</pre> | no |
| <a name="input_aws_cidr_subnets_public"></a> [aws\_cidr\_subnets\_public](#input\_aws\_cidr\_subnets\_public) | CIDR Blocks for public subnets in Availability Zones | `list(string)` | <pre>[<br>  "10.250.224.0/20"<br>]</pre> | no |
| <a name="input_aws_etcd_disk_size"></a> [aws\_etcd\_disk\_size](#input\_aws\_etcd\_disk\_size) | Disk size for etcd Nodes (in GiB) | `number` | `50` | no |
| <a name="input_aws_etcd_num"></a> [aws\_etcd\_num](#input\_aws\_etcd\_num) | Number of etcd Nodes | `number` | `0` | no |
| <a name="input_aws_etcd_size"></a> [aws\_etcd\_size](#input\_aws\_etcd\_size) | Instance size of etcd Nodes | `string` | `"t3.medium"` | no |
| <a name="input_aws_kube_master_disk_size"></a> [aws\_kube\_master\_disk\_size](#input\_aws\_kube\_master\_disk\_size) | Disk size for Kubernetes Master Nodes (in GiB) | `number` | `50` | no |
| <a name="input_aws_kube_master_num"></a> [aws\_kube\_master\_num](#input\_aws\_kube\_master\_num) | Number of Kubernetes Master Nodes | `number` | `3` | no |
| <a name="input_aws_kube_master_size"></a> [aws\_kube\_master\_size](#input\_aws\_kube\_master\_size) | Instance size of Kube Master Nodes | `string` | `"t3.medium"` | no |
| <a name="input_aws_kube_worker_data_disk_size"></a> [aws\_kube\_worker\_data\_disk\_size](#input\_aws\_kube\_worker\_data\_disk\_size) | Additional Disk size for Kubernetes Worker Nodes (in GiB) | `number` | `100` | no |
| <a name="input_aws_kube_worker_disk_size"></a> [aws\_kube\_worker\_disk\_size](#input\_aws\_kube\_worker\_disk\_size) | Disk size for Kubernetes Worker Nodes (in GiB) | `number` | `50` | no |
| <a name="input_aws_kube_worker_num"></a> [aws\_kube\_worker\_num](#input\_aws\_kube\_worker\_num) | Number of Kubernetes Worker Nodes | `number` | `5` | no |
| <a name="input_aws_kube_worker_size"></a> [aws\_kube\_worker\_size](#input\_aws\_kube\_worker\_size) | Instance size of Kubernetes Worker Nodes | `string` | `"t3.medium"` | no |
| <a name="input_aws_nlb_api_port"></a> [aws\_nlb\_api\_port](#input\_aws\_nlb\_api\_port) | Port for AWS NLB | `number` | `6443` | no |
| <a name="input_aws_vpc_cidr_block"></a> [aws\_vpc\_cidr\_block](#input\_aws\_vpc\_cidr\_block) | CIDR Block for VPC | `string` | `"10.250.192.0/18"` | no |
| <a name="input_encryption_key_arn"></a> [encryption\_key\_arn](#input\_encryption\_key\_arn) | AWS encryption key arn | `any` | n/a | yes |
| <a name="input_env"></a> [env](#input\_env) | Environment name | `string` | n/a | yes |
| <a name="input_inventory_file"></a> [inventory\_file](#input\_inventory\_file) | Where to store the generated inventory file | `string` | `"hosts"` | no |
| <a name="input_k8s_secure_api_port"></a> [k8s\_secure\_api\_port](#input\_k8s\_secure\_api\_port) | Secure Port of K8S API Server | `number` | `6443` | no |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | Project name | `string` | n/a | yes |
| <a name="input_ssh_key_name"></a> [ssh\_key\_name](#input\_ssh\_key\_name) | Name of the SSH keypair to use in AWS. | `string` | `"tucana"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_aws_nlb_api_fqdn"></a> [aws\_nlb\_api\_fqdn](#output\_aws\_nlb\_api\_fqdn) | n/a |
| <a name="output_bastion_ip"></a> [bastion\_ip](#output\_bastion\_ip) | n/a |
| <a name="output_etcd"></a> [etcd](#output\_etcd) | n/a |
| <a name="output_inventory"></a> [inventory](#output\_inventory) | n/a |
| <a name="output_masters"></a> [masters](#output\_masters) | n/a |
| <a name="output_private_ssh_key"></a> [private\_ssh\_key](#output\_private\_ssh\_key) | n/a |
| <a name="output_public_ssh_key"></a> [public\_ssh\_key](#output\_public\_ssh\_key) | n/a |
| <a name="output_workers"></a> [workers](#output\_workers) | n/a |
