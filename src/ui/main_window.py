import os
import sys

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTabWidget

from src.core.i18n import i18n
from src.ui.comic_tab import ComicFolderTab
from src.ui.ebook_tab import EbookTab
from src.ui.extract_tab import ExtractTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(i18n.get("app_title"))
        self.resize(980, 700)
        self.center_window()

        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.comic_tab = ComicFolderTab()
        self.ebook_tab = EbookTab()
        self.extract_tab = ExtractTab()

        self.tabs.addTab(self.comic_tab, i18n.get("tab_folder_to_fmt"))
        self.tabs.addTab(self.ebook_tab, i18n.get("tab_fmt_to_fmt"))
        self.tabs.addTab(self.extract_tab, i18n.get("tab_extract"))

        self.create_menu()

        self.statusBar().showMessage(i18n.get("ready"))
        self.tabs.currentChanged.connect(self.on_tab_changed)

        i18n.add_listener(self.update_texts)

        self.apply_styles()

    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def create_menu(self):
        menu_bar = self.menuBar()
        menu_bar.clear()

        lang_menu = menu_bar.addMenu(i18n.get("menu_language"))

        action_en = QAction("English", self)
        action_en.triggered.connect(lambda: i18n.set_lang("en"))
        lang_menu.addAction(action_en)

        action_zh = QAction("中文", self)
        action_zh.triggered.connect(lambda: i18n.set_lang("zh"))
        lang_menu.addAction(action_zh)

        help_menu = menu_bar.addMenu(i18n.get("menu_help"))

        action_about = QAction(i18n.get("menu_about"), self)
        action_about.triggered.connect(self.show_about)
        help_menu.addAction(action_about)

    def update_texts(self):
        self.setWindowTitle(i18n.get("app_title"))
        self.tabs.setTabText(0, i18n.get("tab_folder_to_fmt"))
        self.tabs.setTabText(1, i18n.get("tab_fmt_to_fmt"))
        self.tabs.setTabText(2, i18n.get("tab_extract"))

        self.statusBar().showMessage(i18n.get("ready"))
        self.create_menu()

    def on_tab_changed(self, _index):
        self.statusBar().showMessage(i18n.get("ready"))

    def show_about(self):
        QMessageBox.about(self, i18n.get("menu_about"), i18n.get("about_msg"))

    def apply_styles(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f3f5f8;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
                font-size: 14px;
            }

            QMenuBar {
                background: #ffffff;
                border-bottom: 1px solid #d8dee9;
            }
            QMenuBar::item {
                background: transparent;
                padding: 6px 10px;
            }
            QMenuBar::item:selected {
                background: #eaf1fb;
                border-radius: 4px;
            }

            QStatusBar {
                background: #ffffff;
                border-top: 1px solid #d8dee9;
                color: #455468;
            }

            QTabWidget::pane {
                border: 1px solid #d7deea;
                background: #ffffff;
                border-radius: 10px;
                top: -1px;
            }
            QTabBar::tab {
                background: #e9edf4;
                color: #4a5b73;
                padding: 10px 18px;
                margin-right: 6px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #0a5ec2;
                border-bottom: 2px solid #0a5ec2;
            }
            QTabBar::tab:hover:!selected {
                background: #dde5f1;
            }

            QPushButton {
                background-color: #0a5ec2;
                color: #ffffff;
                border: none;
                padding: 8px 14px;
                border-radius: 7px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0853ab;
            }
            QPushButton:pressed {
                background-color: #074387;
            }
            QPushButton:disabled {
                background-color: #c7d0de;
                color: #7a8799;
            }

            QLineEdit {
                padding: 8px;
                border: 1px solid #cfd7e4;
                border-radius: 7px;
                background: #ffffff;
                selection-background-color: #0a5ec2;
            }
            QLineEdit:focus {
                border: 1px solid #0a5ec2;
            }

            QGroupBox {
                font-weight: 600;
                border: 1px solid #d9e0ec;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 22px;
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
                color: #2d3a4d;
                background-color: #ffffff;
            }

            QRadioButton, QCheckBox {
                spacing: 8px;
                color: #2d3a4d;
            }
            QRadioButton::indicator, QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }

            QProgressBar {
                border: none;
                background-color: #e4eaf3;
                border-radius: 6px;
                text-align: center;
                color: #2d3a4d;
                font-weight: 600;
            }
            QProgressBar::chunk {
                background-color: #23a35e;
                border-radius: 6px;
            }

            QLabel {
                color: #2d3a4d;
            }

            QTextEdit {
                border: 1px solid #d0d8e4;
                border-radius: 7px;
                background-color: #f7f9fc;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
                padding: 8px;
            }

            QTableWidget {
                border: 1px solid #d0d8e4;
                border-radius: 7px;
                background-color: #ffffff;
                gridline-color: #e8edf5;
            }
            QHeaderView::section {
                background: #f2f5fb;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #d9e0ec;
                color: #4a5b73;
                font-weight: 600;
            }
            """
        )


def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
