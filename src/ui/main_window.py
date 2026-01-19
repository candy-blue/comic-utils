import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinterdnd2 import TkinterDnD
from src.ui.comic_tab import ComicFolderTab
from src.ui.ebook_tab import EbookTab
from src.core.i18n import i18n
from tkinter import messagebox

class MainWindow(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        
        # Apply theme
        self.style = ttk.Style(theme="cosmo")
        
        self.title(i18n.get('app_title'))
        self.geometry("900x650")
        
        # Menu
        self.create_menu()
        
        # Center window
        self.center_window()
        
        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add Tabs
        self.comic_tab = ComicFolderTab(self.notebook)
        self.ebook_tab = EbookTab(self.notebook)
        
        self.notebook.add(self.comic_tab, text=i18n.get('tab_comic'))
        self.notebook.add(self.ebook_tab, text=i18n.get('tab_ebook'))
        
        # Listen for language changes to update title/tabs
        i18n.add_listener(self.update_texts)

    def create_menu(self):
        menubar = tk.Menu(self)
        
        # Language Menu
        lang_menu = tk.Menu(menubar, tearoff=0)
        lang_menu.add_command(label="English", command=lambda: i18n.set_lang('en'))
        lang_menu.add_command(label="中文", command=lambda: i18n.set_lang('zh'))
        menubar.add_cascade(label=i18n.get('menu_language'), menu=lang_menu)
        self.lang_menu_ref = menubar # Reference to update label later? 
        # Actually tk menu labels are hard to update dynamically without recreating, 
        # but we can try referencing the cascade index.
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=i18n.get('menu_about'), command=self.show_about)
        menubar.add_cascade(label=i18n.get('menu_help'), menu=help_menu)
        
        self.config(menu=menubar)
        self.menubar = menubar

    def update_texts(self):
        self.title(i18n.get('app_title'))
        self.notebook.tab(0, text=i18n.get('tab_comic'))
        self.notebook.tab(1, text=i18n.get('tab_ebook'))
        
        # Recreate menu to update labels
        self.create_menu()

    def show_about(self):
        messagebox.showinfo(i18n.get('menu_about'), i18n.get('about_msg'))

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
