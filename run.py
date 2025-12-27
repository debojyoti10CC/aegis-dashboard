#!/usr/bin/env python3
"""
Quick start script for the Disaster Management System
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from disaster_management_system.cli.main import main

if __name__ == '__main__':
    sys.exit(main())