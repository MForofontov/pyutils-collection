"""Backward-compatible import for the command-line SSH helper."""

from .local.ssh_execute_script import ssh_execute_script

__all__ = ["ssh_execute_script"]
