resource "aws_instance" "this" {
  for_each = var.servidores
  ami = var.ami_id
  instance_type = each.value.type
  key_name = var.key_name
  subnet_id = each.value.subnet == "public" ? var.public_subnet_id : var.private_subnet_id
  vpc_security_group_ids = [var.security_group_id]

  tags = {
    Name = "${var.environment}-${each.key}"
    Role = "web"
    Owner = var.owner
    Environment = var.environment
    nginx = tostring(each.value.nginx)
  }
  
}