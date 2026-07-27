terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "kubernetes" {
  config_path = "C:/Users/prezido/Desktop/Devops/ec2-k8s-cluster/ec2-kubeconfig"
}

provider "helm" {
  kubernetes = {
    config_path = "C:/Users/prezido/Desktop/Devops/ec2-k8s-cluster/ec2-kubeconfig"
  }
}