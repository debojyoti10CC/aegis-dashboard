#!/usr/bin/env python3
"""
Vercel-compatible Flask app for Disaster Management System
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the Flask app from frontend
from frontend.app import app

# Vercel expects the app to be available as 'app'
if __name__ == "__main__":
    app.run()