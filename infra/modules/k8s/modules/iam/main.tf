#Add AWS Roles for Kubernetes

resource "aws_iam_role" "kube_control_plane" {
  name = "kubernetes-${var.aws_cluster_name}-master"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      }
      }
  ]
}
EOF
}

resource "aws_iam_role" "kube-worker" {
  name = "kubernetes-${var.aws_cluster_name}-node"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      }
      }
  ]
}
EOF
}

#Add AWS Policies for Kubernetes

resource "aws_iam_role_policy" "kube_control_plane" {
  name = "kubernetes-${var.aws_cluster_name}-master"
  role = aws_iam_role.kube_control_plane.id
  #tfsec:ignore:aws-iam-no-policy-wildcards
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "ecr:GetAuthorizationToken",
            "ecr:BatchCheckLayerAvailability",
            "ecr:GetDownloadUrlForLayer",
            "ecr:GetRepositoryPolicy",
            "ecr:DescribeRepositories",
            "ecr:ListImages",
            "ecr:BatchGetImage"
          ],
          "Resource": "*"
        }
      ]
}
EOF
}

resource "aws_iam_role_policy" "kube-worker" {
  name = "kubernetes-${var.aws_cluster_name}-node"
  role = aws_iam_role.kube-worker.id
  #tfsec:ignore:aws-iam-no-policy-wildcards
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "ecr:GetAuthorizationToken",
            "ecr:BatchCheckLayerAvailability",
            "ecr:GetDownloadUrlForLayer",
            "ecr:GetRepositoryPolicy",
            "ecr:DescribeRepositories",
            "ecr:ListImages",
            "ecr:BatchGetImage"
          ],
          "Resource": "*"
        }
      ]
}
EOF
}

#Create AWS Instance Profiles

resource "aws_iam_instance_profile" "kube_control_plane" {
  name = "kube_${var.aws_cluster_name}_master_profile"
  role = aws_iam_role.kube_control_plane.name
}

resource "aws_iam_instance_profile" "kube-worker" {
  name = "kube_${var.aws_cluster_name}_node_profile"
  role = aws_iam_role.kube-worker.name
}
