terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend configuration for state storage
  # Uncomment and configure for production
  # backend "s3" {
  #   bucket = "docuchat-terraform-state"
  #   key    = "prod/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region
}

# VPC and networking resources
module "vpc" {
  source = "./modules/vpc"
  
  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

# RDS PostgreSQL with pgvector
module "database" {
  source = "./modules/rds"
  
  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnet_ids
  
  instance_class      = var.db_instance_class
  allocated_storage   = var.db_allocated_storage
  database_name       = var.db_name
  master_username     = var.db_username
}

# ECS Cluster for container orchestration
module "ecs" {
  source = "./modules/ecs"
  
  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnet_ids
}

# TODO: Add modules for:
# - ALB (Application Load Balancer)
# - ECS Services (backend, frontend)
# - CloudFront distribution
# - Route53 DNS
# - ACM certificates
# - CloudWatch logging
# - S3 buckets for static assets
