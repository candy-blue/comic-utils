import tkinter as tk
from tkinter import ttk
from src.ui.comic_tab import ComicFolderTab
from src.ui.ebook_tab import EbookTab

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Comic Utilities")
        self.geometry("850x600")
        
        # Center window
        self.center_window()
        
        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add Tabs
        self.comic_tab = ComicFolderTab(self.notebook)
        self.ebook_tab = EbookTab(self.notebook)
        
        self.notebook.add(self.comic_tab, text="Comic Folder to CBZ")
        self.notebook.add(self.ebook_tab, text="Ebook (epub/mobi) to CBZ")
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

def run_gui():
    app = MainWindow()
    app.mainloop()
