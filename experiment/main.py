"""
Bill Splitter Application - Main Entry Point
Coordinates the application flow and initializes components.
"""
import pygame
import sys
from ui_manager import UIManager

def main():
    """Initialize and run the Bill Splitter application."""
    pygame.init()
    
    try:
        app = UIManager()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()