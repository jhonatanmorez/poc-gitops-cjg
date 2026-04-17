module "network" {
  source = "../../modules/vpc"
  vpc_cidr = "10.0.0.0/16"
  public_cidr = "10.0.1.0/24"
  private_cidr = "10.0.2.0/24"
  environment = "dev"
}

module "compute" {
  source = "../../../modules/ec2"
  environment = "dev"
  owner       = "demo1"
  ami_id      = "ami-04680790a315cd58d"
  key_name    = "ec2keypair"
  public_subnet_id  = module.network.public_subnet_id
  private_subnet_id = module.network.private_subnet_id

    servidores = {
    web01 = {
      instance_type = "t3.micro"
      role          = "web"
      nginx         = true
    }
  }
}


