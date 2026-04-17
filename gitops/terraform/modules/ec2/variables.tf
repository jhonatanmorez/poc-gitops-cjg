variable "servidores" {
  description = "Información de los servidores a crear"
  type = map(object({
    instance_type = string
    subnet_id    = string
    nginx         = bool
    role          = string  
  }))
}

variable "ami_id" {
  description = "ID de la AMI a usar para las instancias"
  type        = string
}

variable "key_name" {
  description = "Nombre del par de claves para acceder a las instancias"
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
variable "public_subnet_id" {
  description = "ID de la subred pública"
  type        = string
}   

variable "private_subnet_id" {
  description = "ID de la subred privada"
  type        = string
}   

