# Complete DevOps CI/CD Pipeline on Kubernetes

## Project Overview

This project is a fully automated CI/CD and GitOps pipeline that builds a Python Flask application, containerizes it, and deploys it to a self-hosted Kubernetes cluster running on AWS EC2. A code push triggers an automated chain: Docker image build, push to Docker Hub, Helm chart update, and an Argo CD sync that deploys the new version to the cluster, all without any manual deployment step.

The cluster itself is provisioned entirely with Terraform, and instead of a managed Kubernetes service or a local tool like Minikube, it runs Canonical's k8s-snap on a plain EC2 instance. That choice, and the reasoning behind it, is covered below.

## Architecture

```
Developer
   │  git push
   ▼
GitHub
   │  triggers
   ▼
GitHub Actions
   │  build + tag + push image
   ▼
Docker Hub
   │  Helm chart values.yaml updated with new image tag, committed back to GitHub
   ▼
Argo CD (running inside the cluster, watching the GitHub repo)
   │  detects the commit, syncs automatically
   ▼
Kubernetes Cluster (EC2 + k8s-snap, provisioned by Terraform)
   │
   ▼
Running Application
```

<img width="1361" height="672" alt="Screenshot 2026-07-27 224050" src="https://github.com/user-attachments/assets/77856f87-4b06-4e19-914a-fb5a20835882" />

## Technologies Used

- Python (Flask)
- Docker
- GitHub Actions
- Terraform
- AWS EC2, IAM, Security Groups
- Kubernetes (via Canonical's k8s-snap)
- Helm
- Argo CD
- Docker Hub

## Features

- Infrastructure provisioned entirely as code, including the EC2 instance, security group, and SSH key pair
- Automatic Kubernetes cluster bootstrap on first boot, with zero manual setup steps, via an EC2 user-data script
- Containerized Flask application with a health check endpoint
- Continuous integration via GitHub Actions: build, tag with commit SHA, push to Docker Hub
- Automated Helm chart updates on every push, committed back to the repository
- GitOps deployment via Argo CD, with automated sync and self-healing enabled
- Kubernetes deployment packaged and managed with Helm rather than raw manifests

## Project Structure

```
.
├── main.tf                  # EC2 instance, security group, key pair, AMI lookup
├── variables.tf              # Input variables (region, instance type, IP allowlist)
├── provider.tf                # AWS, Kubernetes, and Helm provider configuration
├── backend.tf                 # Terraform state backend configuration
├── outputs.tf                  # Public IP and SSH command outputs
├── user-data.sh                 # EC2 bootstrap script — installs and starts k8s-snap
├── agro cd.tf                    # Argo CD installation via Terraform's Helm provider
├── argocd-app.yaml                 # Argo CD Application resource, points at the Helm chart below
├── app.py                          # Flask application
├── Dockerfile                      # Container build instructions
├── complete-dev-project/           # Helm chart for the Flask application
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
└── .github/
    └── workflows/
        └── ci.yaml                 # CI/CD pipeline definition
```

## Prerequisites

- AWS account with a paid (non-Free Plan) billing tier, and an IAM user with EC2 permissions
- Terraform CLI
- Helm CLI
- Git
- Docker Hub account, with an access token stored as a GitHub Actions secret
- A GitHub personal access token, for Argo CD to authenticate to the repository

## Installation

```bash
git clone https://github.com/Prezido29/Fully-Automated-DevOps-Pipeline-from-Scratch
cd Fully-Automated-DevOps-Pipeline-from-Scratch

terraform init
terraform apply
```

The `apply` step provisions the EC2 instance and, via its user-data script, automatically installs and bootstraps the Kubernetes cluster on first boot. Give it a few minutes after the instance launches before connecting, since the cluster bootstrap runs in the background.



## Configuration

The following are required, either as `terraform.tfvars` values or GitHub Actions secrets:

| Variable | Where it's used | Purpose |
|---|---|---|
| `my_ip` | `variables.tf` | Restricts SSH and Kubernetes API access to a specific IP |
| `instance_type` | `variables.tf` | EC2 instance size (minimum 8GB RAM for k8s-snap) |
| `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` | GitHub Actions secrets | Docker Hub authentication for image pushes |

## Deployment

1. Code is pushed to the `main` branch on GitHub
2. GitHub Actions checks out the code, builds a Docker image tagged with the commit's short SHA, and pushes it to Docker Hub
3. The workflow updates the image tag inside the Helm chart's `values.yaml`, then commits and pushes that change back to the repository
4. Argo CD, continuously watching the repository, detects the new commit
5. Argo CD automatically syncs the cluster, deploying the new image with zero manual intervention

<img width="1341" height="575" alt="Screenshot 2026-07-28 003945" src="https://github.com/user-attachments/assets/bb869566-fbe2-41b3-a939-6b3cbcc14b60" />


## CI/CD Pipeline

```
Developer Push
      │
      ▼
GitHub Actions triggered
      │
      ▼
Docker Build (tagged with commit SHA)
      │
      ▼
Push to Docker Hub
      │
      ▼
Update Helm Chart values.yaml
      │
      ▼
Commit and Push to GitHub
      │
      ▼
Argo CD detects change
      │
      ▼
Argo CD Sync
      │
      ▼
Kubernetes Deployment (new ReplicaSet, new Pod)
```

## Infrastructure

Terraform provisions:

- An EC2 instance (Ubuntu, sized for k8s-snap's 8GB RAM minimum)
- A security group allowing SSH, the Kubernetes API port, and a NodePort range
- An SSH key pair, generated and managed entirely through Terraform
- The Argo CD Helm release, installed directly into the cluster via Terraform's Helm provider

The EC2 instance's own bootstrap (installing k8s-snap and starting the cluster) runs through a `user-data` script, executed automatically by AWS on first boot.

## Engineering Decisions

**EC2 with k8s-snap instead of Minikube.** The original approach was Minikube running locally via Docker Desktop, following a standard tutorial pattern. My laptop couldn't run Docker Desktop and Minikube together without severe resource strain. Rather than working around that constraint locally, I moved the cluster to a cloud instance, which also meant the Terraform, security, and networking concerns became closer to a real production setup than a local demo would have been.

**Helm instead of raw Kubernetes manifests.** Raw manifests would have meant duplicating YAML for every environment or configuration change. Helm's templating, with a single `values.yaml` controlling image tags, replica counts, and service configuration, made the same chart reusable and let the CI pipeline update one value on every deploy instead of rewriting manifests.

**Argo CD for GitOps instead of a pipeline that deploys directly.** A pipeline that runs `kubectl apply` directly needs cluster credentials inside CI, which is a meaningful security surface to manage. Argo CD instead runs inside the cluster and pulls from Git on its own schedule, so the CI pipeline only ever needs permission to push to the repository, never direct access to the cluster itself. It also means the cluster continuously reconciles itself to match Git, including self-healing if something drifts from what's declared.

**Terraform's Helm provider to install Argo CD, rather than a manual `helm install`.** Keeping Argo CD's own installation in Terraform, alongside the EC2 instance itself, means the entire stack, infrastructure and the GitOps tooling on top of it, is defined in one place and rebuildable from a single `terraform apply`.

## Challenges and Solutions

**State drift after manual and automated rebuilds.** Across several rebuild cycles, Terraform's state file lost track of resources that were still genuinely running in AWS, in one case an EC2 instance and security group, in another a Helm release. Both times, `terraform plan` surfaced the mismatch as an unexpected creation of something that already existed. Resolved with `terraform import`, reconciling Terraform's state with the real infrastructure rather than letting `apply` create duplicates.

**TLS certificate rejecting the cluster's public IP.** After correctly pointing the kubeconfig at the instance's public IP and the correct API port, connections still failed with a certificate error. The cluster's API server certificate, generated automatically at bootstrap, only listed the private/internal addresses it knew about at that time, and had no way of knowing a public IP would later be used to reach it. Resolved by running `k8s refresh-certs --extra-sans` to add the public IP to the certificate's list of valid addresses, then re-pulling a fresh kubeconfig.


## Future Improvements

- Add Prometheus and Grafana for cluster and application monitoring
- Add a Horizontal Pod Autoscaler for the Flask deployment
- Bake environment bootstrap steps (Argo CD CLI install, certificate SAN refresh) into `user-data.sh`, so a full rebuild requires no manual post-apply steps
- Add automated security scanning to the CI pipeline
- Migrate from a single self-managed EC2 node to Amazon EKS for a managed control plane

## License

MIT License

## Author

Prezido

- GitHub: [Prezido29](https://github.com/Prezido29)
- LinkedIn: https://www.linkedin.com/in/mba-ikechukwu
