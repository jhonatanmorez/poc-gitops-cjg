resource "aws_instance" "this" {
  for_each = var.servidores
  ami = var.ami_id
  instance_type = each.value.instance_type
  key_name = "ec2keypair"
  subnet_id = each.value.role == "web" ? var.public_subnet_id : var.private_subnet_id

  tags = {
    Name = "${var.environment}-${each.key}"
    Role = each.value.role
    Owner = var.owner
    Environment = var.environment
    nginx = each.value.nginx ? "true" : "false"
  }
}