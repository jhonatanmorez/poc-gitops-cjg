provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "web" {
  ami           = "ami-04680790a315cd58d"
  instance_type = "t3.micro"

  tags = {
    Name = "web01"
    Role = "web"
    Owner = "demo1"
    Environment = "dev"
  }
}

resource "local_file" "ansible_inventory" {
  content  = <<EOT
all:
  hosts:
    webserver:
      ansible_host: ${aws_instance.web.public_ip}
      ansible_user: ubuntu
EOT
  filename = "../ansible/inventory.yml"
}