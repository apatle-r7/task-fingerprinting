# Expose modules under fingerprint.products so callers can import
# `from fingerprint.products import vscode`.
from . import vs as vscode

__all__ = ["vscode"]