#!/bin/bash
set -e

# Install k8s snap
snap install k8s --classic --channel=1.32-classic/stable

# Bootstrap the single-node cluster
k8s bootstrap

# Wait until the cluster is fully ready
k8s status --wait-ready

# Make kubectl usable for the ubuntu user without sudo
mkdir -p /home/ubuntu/.kube
k8s kubectl config view --raw > /home/ubuntu/.kube/config
chown -R ubuntu:ubuntu /home/ubuntu/.kube