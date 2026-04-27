#!/usr/bin/env python3
"""CareerAssistant Pro - Main Entry Point"""
import sys
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.cli import main

if __name__ == "__main__":
    main()
