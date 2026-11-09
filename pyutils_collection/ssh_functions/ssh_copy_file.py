"""Backward-compatible import for the command-line SSH helper."""

from .local.ssh_copy_file import ssh_copy_file

__all__ = ["ssh_copy_file"]
