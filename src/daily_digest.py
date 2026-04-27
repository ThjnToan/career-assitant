#!/usr/bin/env python3
"""Daily digest script - run this every morning for updates."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import init_db
from src.notifier import get_daily_digest, format_digest, check_and_notify
from rich.console import Console

console = Console()

def main():
    init_db()
    digest = get_daily_digest()
    console.print(format_digest(digest))
    check_and_notify()

if __name__ == "__main__":
    main()
