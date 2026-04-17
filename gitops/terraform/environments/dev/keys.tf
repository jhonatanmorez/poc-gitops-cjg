# Generar la clave SSH localmente
resource "tls_private_key" "ec2" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Crear la clave pública en AWS
resource "aws_key_pair" "ec2" {
  key_name   = "ec2keypair"
  public_key = tls_private_key.ec2.public_key_openssh
}

# Guardar la clave privada localmente
resource "local_file" "private_key" {
  content  = tls_private_key.ec2.private_key_pem
  filename = "${path.module}/../../../ec2-key.pem"

  file_permission = "0600"
}
