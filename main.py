import sys
import os

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.main_window import run_gui

if __name__ == "__main__":
    run_gui()
