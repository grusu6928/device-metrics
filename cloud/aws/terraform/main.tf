# AWS Infrastructure for Device Metrics Service
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# EKS Cluster for Kubernetes
resource "aws_eks_cluster" "device_metrics" {
  name     = "device-metrics-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.28"

  vpc_config {
    subnet_ids = aws_subnet.main[*].id
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "postgres" {
  identifier           = "device-metrics-db"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.medium"
  allocated_storage    = 100
  storage_encrypted    = true
  db_name              = "device_metrics"
  username             = var.db_username
  password             = var.db_password
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  backup_retention_period = 7
  skip_final_snapshot     = true
}

# MSK (Managed Kafka)
resource "aws_msk_cluster" "kafka" {
  cluster_name           = "device-metrics-kafka"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 3

  broker_node_group_info {
    instance_type   = "kafka.m5.large"
    client_subnets  = aws_subnet.main[*].id
    security_groups = [aws_security_group.kafka.id]
    storage_info {
      ebs_storage_info {
        volume_size = 100
      }
    }
  }

  encryption_info {
    encryption_at_rest_kms_key_id = aws_kms_key.kafka.arn
  }
}

# S3 Bucket for Metric Archives
resource "aws_s3_bucket" "metrics_archive" {
  bucket = "${var.project_name}-metrics-archive"

  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_s3_bucket_versioning" "metrics_archive" {
  bucket = aws_s3_bucket.metrics_archive.id
  versioning_configuration {
    status = "Enabled"
  }
}

# IAM Roles and Policies
resource "aws_iam_role" "eks_cluster" {
  name = "device-metrics-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

# Outputs
output "eks_cluster_endpoint" {
  value = aws_eks_cluster.device_metrics.endpoint
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.endpoint
}

output "kafka_brokers" {
  value = aws_msk_cluster.kafka.bootstrap_brokers
}

output "s3_bucket_name" {
  value = aws_s3_bucket.metrics_archive.id
}

