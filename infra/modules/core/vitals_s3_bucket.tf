# Patient vitals
resource "aws_s3_bucket" "vitals" {
  bucket = "${var.env}-vitals"
}

resource "aws_s3_bucket_public_access_block" "vitals" {
  bucket = aws_s3_bucket.vitals.id

  restrict_public_buckets = true
  block_public_policy     = true
  block_public_acls       = true
  ignore_public_acls      = true
}

resource "aws_s3_bucket_versioning" "vitals" {
  bucket = aws_s3_bucket.vitals.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "vitals" {
  bucket = aws_s3_bucket.vitals.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.core_encryption_key.id
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_logging" "vitals" {
  bucket = aws_s3_bucket.vitals.id

  target_bucket = aws_s3_bucket.vitals.id
  target_prefix = "log/"
}

resource "aws_s3_bucket_lifecycle_configuration" "vitals" {
  bucket = aws_s3_bucket.vitals.id

  rule {
    id     = "archival"
    status = "Enabled"
    filter {
      prefix = "hospitals/"
    }
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

resource "aws_iam_group" "hospitals" {
  name = "hospitals"
}

resource "aws_iam_user" "hospitals" {
  for_each = toset(var.vitals_bucket_users)
  name     = each.value
}

resource "aws_iam_group_membership" "hospitals" {
  name  = "hospitals"
  users = var.vitals_bucket_users
  group = aws_iam_group.hospitals.name

  depends_on = [
    aws_iam_user.hospitals
  ]
}

resource "aws_iam_group_policy" "hospital_vitals_upload" {
  name  = "${var.env}-vitals-upload"
  group = aws_iam_group.hospitals.name
  # tfsec:ignore:aws-iam-no-policy-wildcards
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["${aws_s3_bucket.vitals.arn}"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:AbortMultipartUpload"
      ],
      "Resource": ["${aws_s3_bucket.vitals.arn}/hospitals/*"]
    },
		{
			"Effect": "Allow",
			"Action": [
				"kms:Decrypt",
				"kms:GenerateDataKey"
			],
			"Resource": "${aws_kms_key.core_encryption_key.arn}"
		}
  ]
}
EOF
}