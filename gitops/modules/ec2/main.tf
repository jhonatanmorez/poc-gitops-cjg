variable "name" {}
variable "instance_type" {}
variable "environment" {}
variable "owner" {}

data "aws_ami" "latest" {
  most_recent = true
  owners      = ["amazon"]
}

resource "aws_instance" "this" {
  ami           = data.aws_ami.latest.id
  instance_type = var.instance_type

  tags = {
    Name        = var.name
    Environment = var.environment
    Owner       = var.owner
  }
}