"""Backward-compatible import for the command-line SSH helper."""

from .local.ssh_execute_command import ssh_execute_command

__all__ = ["ssh_execute_command"]
