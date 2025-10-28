#!/usr/bin/env python3
"""Entry point for Chi2 Mage bot."""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.bots.chi2.runner_mage import main

if __name__ == '__main__':
    main()
