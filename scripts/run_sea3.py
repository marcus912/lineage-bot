#!/usr/bin/env python3
"""Entry point for Sea3 bot."""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.bots.sea3.runner import main

if __name__ == '__main__':
    main()
