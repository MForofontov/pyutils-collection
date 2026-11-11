"""Backward-compatible import for the command-line SSH helper."""

from .local.ssh_check_connection import ssh_check_connection

__all__ = ["ssh_check_connection"]
