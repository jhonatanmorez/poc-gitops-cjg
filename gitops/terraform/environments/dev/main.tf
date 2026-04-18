module "network" {
  source = "../../modules/vpc"

  vpc_cidr     = "10.0.0.0/16"
  public_cidr  = "10.0.1.0/24"
  private_cidr = "10.0.2.0/24"

  environment = "dev"
}

module "security" {
  source = "../../modules/sg"

  vpc_id      = module.network.vpc_id
  environment = "dev"
  owner       = "cjg"
  sg_name     = "web-sg"
}

module "compute" {
  source = "../../modules/ec2"

  servidores = {
    "web-1" = {
      type = "t2.micro"
      subnet = "public"
      role  = "web"
      nginx = true
    }
  }

  ami_id            = "ami-04680790a315cd58d"
  key_name          = "ec2keypair"
  security_group_id = module.security.security_group_id
  public_subnet_id  = module.network.public_subnet_id
  private_subnet_id = module.network.private_subnet_id

  environment = "dev"
  owner       = "cjg"
}

