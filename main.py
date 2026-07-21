"""
Main Entry Point.
This file is the very first thing that runs. It ensures the database is setup,
starts the assistant engine, and handles graceful shutdown.
"""

from database import create_tables
from assistant import start_assistant
import sys

def main():
    print("Initializing AI Desktop Voice Assistant...")
    
    # 1. Setup the database if it's the first time running
    print("Checking database...")
    create_tables()
    
    # 2. Start the core assistant loop
    print("Starting the assistant engine...")
    try:
        start_assistant()
    except KeyboardInterrupt:
        print("\nAssistant stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"\nA critical error occurred: {e}")
    finally:
        print("Assistant successfully shut down.")
        sys.exit(0)

if __name__ == "__main__":
    main()
