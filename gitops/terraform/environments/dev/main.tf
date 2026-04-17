module "network" {
  source = "../../modules/vpc"

  vpc_cidr     = "10.0.0.0/16"
  public_cidr  = "10.0.1.0/24"
  private_cidr = "10.0.2.0/24"

  environment = "dev"
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

  ami_id            = "ami-0c02fb55956c7d316"
  key_name          = "ec2keypair"
  security_group_id = "sg-0259ad317a15a31c3"
  public_subnet_id  = module.network.public_subnet_id
  private_subnet_id = module.network.private_subnet_id

  environment = "dev"
  owner       = "cjg"
}

