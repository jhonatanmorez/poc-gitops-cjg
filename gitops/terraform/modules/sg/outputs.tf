output "security_group_id" {
  description = "ID del security group creado"
  value       = aws_security_group.this.id
}

output "security_group_name" {
  description = "Nombre del security group"
  value       = aws_security_group.this.name
}
