variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type — needs 8GB+ RAM for k8s-snap"
  type        = string
  default     = "t3.large"
}

variable "key_name" {
  description = "Name of the EC2 key pair to create/use for SSH"
  type        = string
  default     = "k8s-cluster-key"
}

variable "my_ip" {
  description = "Your IP address in CIDR notation, for SSH/API access (e.g. 1.2.3.4/32)"
  type        = string
  default     = "102.90.115.219/32"
}

variable "volume_size" {
  description = "Root volume size in GB"
  type        = number
  default     = 30
}