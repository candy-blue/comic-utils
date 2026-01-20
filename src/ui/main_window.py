
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox, QMenu
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import os

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
        
        # Set Icon
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
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
        # Enhanced modern style (Material Design inspired)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
                font-size: 14px;
            }
            
            /* Tabs */
            QTabWidget::pane {
                border: 1px solid #e1e4e8;
                background: white;
                border-radius: 8px;
                top: -1px; 
            }
            QTabBar::tab {
                background: #e1e4e8;
                color: #586069;
                padding: 10px 20px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: white;
                color: #0366d6;
                border-bottom: 2px solid #0366d6;
            }
            QTabBar::tab:hover:!selected {
                background: #eaecef;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #0366d6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0256b9;
            }
            QPushButton:pressed {
                background-color: #024494;
            }
            QPushButton:disabled {
                background-color: #94d3a2; /* Light green for disabled start? Or just grey */
                background-color: #d1d5da;
                color: #959da5;
            }
            
            /* Inputs */
            QLineEdit {
                padding: 8px;
                border: 1px solid #d1d5da;
                border-radius: 6px;
                background: white;
                selection-background-color: #0366d6;
            }
            QLineEdit:focus {
                border: 1px solid #0366d6;
                outline: none;
            }
            
            /* GroupBox */
            QGroupBox {
                font-weight: 600;
                border: 1px solid #e1e4e8;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 24px;
                padding-bottom: 12px;
                padding-left: 12px;
                padding-right: 12px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 4px;
                color: #24292e;
                background-color: #ffffff; /* Match groupbox background to hide border behind text */
            }
            
            /* Radio & Checkbox */
            QRadioButton {
                spacing: 8px;
                color: #24292e;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox {
                spacing: 8px;
                color: #24292e;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            
            /* ProgressBar */
            QProgressBar {
                border: none;
                background-color: #e1e4e8;
                border-radius: 6px;
                text-align: center;
                color: #24292e;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #2ea44f;
                border-radius: 6px;
            }
            
            /* Label */
            QLabel {
                color: #24292e;
            }
            
            /* TextEdit (Logs) */
            QTextEdit {
                border: 1px solid #d1d5da;
                border-radius: 6px;
                background-color: #f6f8fa;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
                padding: 8px;
            }
        """)

def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
