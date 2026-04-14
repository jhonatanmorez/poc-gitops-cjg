module "network" {
  source = "../../modules/vpc"
}

module "compute" {
  source = "../../../modules/ec2"
  environment = "dev"
  owner       = "demo1"
  ami_id      = "ami-04680790a315cd58d"
  key_name    = "ec2keypair"
  public_subnet_id  = module.network.public_subnet_id
  private_subnet_id = module.network.private_subnet_id
}

locals {
  servidores = {
    web01 = {
      instance_type = "t3.micro"
      role          = "web"
      nginx         = true
    }
  }
}