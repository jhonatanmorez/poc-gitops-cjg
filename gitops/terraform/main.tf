provider "aws" {
  region = "us-east-1"
}

terraform {
  required_version = ">= 1.0.0"

  backend "s3" {
    bucket         = "poccjg-s3-tf-state"
    key            = "proyectos/web-server/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock" # Evita que dos personas apliquen cambios a la vez
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# 1. Referenciar el Security Group existente (por nombre)
data "aws_security_group" "existing_sg" {
  name = "SG-gitops-runner" # Cambia esto por el nombre real en AWS
}

resource "aws_instance" "web" {
  ami           = "ami-04680790a315cd58d"
  instance_type = "t3.micro"
  
  # 2. Usar tu KeyPair existente
  key_name      = "ec2keypair" # Solo el nombre, sin .pem

  # 3. Asignar el Security Group encontrado
  vpc_security_group_ids = [data.aws_security_group.existing_sg.id]

  tags = {
    Name        = "web01"
    Role        = "web"
    Owner       = "demo1"
    Environment = "dev"
  }
}

