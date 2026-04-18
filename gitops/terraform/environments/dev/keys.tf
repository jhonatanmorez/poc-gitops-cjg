# Referenciar la keypair existente en AWS
data "aws_key_pair" "ec2" {
  key_name = "ec2keypair"
}
