variable "vpc_id" {
  description = "ID de la VPC donde crear el security group"
  type        = string
}

variable "environment" {
  description = "Entorno de despliegue (dev, staging, prod)"
  type        = string
}

variable "owner" {
  description = "Propietario de los recursos"
  type        = string
}

variable "sg_name" {
  description = "Nombre del security group"
  type        = string
  default     = "web-sg"
}
