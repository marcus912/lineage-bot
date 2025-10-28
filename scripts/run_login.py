#!/usr/bin/env python3
"""Entry point for auto login."""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.login.auto_login import login
from time import sleep

if __name__ == '__main__':
    while True:
        login()
        sleep(120)
