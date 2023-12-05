"""Helpers for interacting with Kubernetes"""

import argparse
from mads.cli.command import command


def register_subcommand(parser: argparse.ArgumentParser):
    """Register the kube command"""

    k8scmd = parser.add_subparsers(
        title="Kubernetes commands", help="Available commands"
    )

    @command(k8scmd)
    def rollout(cluster: str, deployment: str, namespace: str):
        """Restart the given deployment."""

        from mads.build import kube

        kube.setup(cluster)
        kube.rollout(deployment, namespace)
