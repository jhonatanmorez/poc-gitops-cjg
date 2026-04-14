terraform {
  required_version = ">= 1.0.0"

  backend "s3" {
    bucket         = "poccjg-s3-tf-state"
    key            = "proyectos/dev/terraform.tfstate"
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