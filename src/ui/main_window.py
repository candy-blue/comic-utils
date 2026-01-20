
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from src.ui.comic_tab import ComicFolderTab
from src.ui.ebook_tab import EbookTab
from src.ui.extract_tab import ExtractTab
from src.core.i18n import i18n

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(i18n.get('app_title'))
        self.resize(900, 650)
        self.center_window()
        
        # Central Widget (Tabs)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Add Tabs
        self.comic_tab = ComicFolderTab()
        self.ebook_tab = EbookTab()
        self.extract_tab = ExtractTab()
        
        self.tabs.addTab(self.comic_tab, i18n.get('tab_folder_to_fmt'))
        self.tabs.addTab(self.ebook_tab, i18n.get('tab_fmt_to_fmt'))
        self.tabs.addTab(self.extract_tab, i18n.get('tab_extract'))
        
        # Menu
        self.create_menu()
        
        # Listen for language changes
        i18n.add_listener(self.update_texts)
        
        # Apply some styles
        self.apply_styles()

    def center_window(self):
        # Center logic is handled by OS usually, or:
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def create_menu(self):
        menu_bar = self.menuBar()
        menu_bar.clear()
        
        # Language Menu
        lang_menu = menu_bar.addMenu(i18n.get('menu_language'))
        
        action_en = QAction("English", self)
        action_en.triggered.connect(lambda: i18n.set_lang('en'))
        lang_menu.addAction(action_en)
        
        action_zh = QAction("中文", self)
        action_zh.triggered.connect(lambda: i18n.set_lang('zh'))
        lang_menu.addAction(action_zh)
        
        # Help Menu
        help_menu = menu_bar.addMenu(i18n.get('menu_help'))
        
        action_about = QAction(i18n.get('menu_about'), self)
        action_about.triggered.connect(self.show_about)
        help_menu.addAction(action_about)

    def update_texts(self):
        self.setWindowTitle(i18n.get('app_title'))
        self.tabs.setTabText(0, i18n.get('tab_folder_to_fmt'))
        self.tabs.setTabText(1, i18n.get('tab_fmt_to_fmt'))
        self.tabs.setTabText(2, i18n.get('tab_extract'))
        
        # Recreate menu to update labels
        self.create_menu()

    def show_about(self):
        QMessageBox.about(self, i18n.get('menu_about'), i18n.get('about_msg'))

    def apply_styles(self):
        # A simple modern dark-ish style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #2196F3;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)

def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
