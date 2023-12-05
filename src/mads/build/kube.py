"""
Helper functions for interacting with Kubernetes.
"""

from .shell import shell


def setup(cluster):
    """Configure kubectl to use the given EKS cluster."""

    shell(f"aws eks update-kubeconfig --name {cluster} --region us-east-1")


def rollout(deployment, namespace):
    """Restart the given deployment."""

    shell(f"kubectl rollout restart deploy/{deployment} -n {namespace}")
