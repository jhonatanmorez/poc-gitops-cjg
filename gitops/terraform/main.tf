



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
    nginx       = "true"
  }
}

