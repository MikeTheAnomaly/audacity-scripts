"""
Audacity Pipe Communication Module

This module provides Python interface for communicating with Audacity through
the mod-script-pipe module using named pipes.

Based on the official Audacity pipe_test.py and pipeclient.py examples.
"""

__version__ = "0.1.0"
__all__ = ["AudacityPipe", "AudacityError"]

from .pipe import AudacityPipe, AudacityError
from .commands import Commands