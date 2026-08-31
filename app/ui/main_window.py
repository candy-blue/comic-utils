import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from qfluentwidgets import (NavigationItemPosition, FluentWindow,
                            SubtitleLabel, setThemeColor, Theme)
                            
from app.ui.pages.home_page import HomePage
from app.ui.pages.pack_page import PackPage
from app.ui.pages.convert_page import ConvertPage
from app.ui.pages.extract_page import ExtractPage
from app.ui.pages.task_page import TaskPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.pages.about_page import AboutPage
from app.config.app_config import cfg
from qfluentwidgets import FluentIcon as FIF

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comic Utils - 漫画工具箱")
        self.resize(1200, 760)
        self.setMinimumSize(960, 640)
        
        # Force navigation panel to expand and hide return button
        self.navigationInterface.setExpandWidth(220)
        self.navigationInterface.setReturnButtonVisible(False)
        
        self.home_interface = HomePage(self)
        self.pack_interface = PackPage(self)
        self.convert_interface = ConvertPage(self)
        self.extract_interface = ExtractPage(self)
        self.task_interface = TaskPage(self)
        self.setting_interface = SettingsPage(self)
        self.about_interface = AboutPage(self)

        self.initNavigation()
        self.initWindow()

        # Listen for theme changes to dynamically update the whole application live without restart
        from qfluentwidgets import qconfig
        qconfig.themeChanged.connect(self._on_theme_changed)

        # Listen for language changes to dynamically update UI text live
        from src.core.i18n import i18n
        i18n.add_listener(self.retranslate)
        self.retranslate()

        # Auto check update if enabled
        if cfg.autoCheckUpdate.value:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.about_interface.check_for_updates(silent=True))

    def _on_theme_changed(self, theme):
        from qfluentwidgets import setTheme
        setTheme(theme)
        self.setBackgroundColor(self._normalBackgroundColor())
        self.update()

    def retranslate(self):
        from src.core.i18n import i18n
        self.setWindowTitle(f"Comic Utils - {i18n.get('app_title')}")
        self.navigationInterface.widget(self.home_interface.objectName()).setText(i18n.get("nav_home"))
        self.navigationInterface.widget(self.pack_interface.objectName()).setText(i18n.get("nav_pack"))
        self.navigationInterface.widget(self.convert_interface.objectName()).setText(i18n.get("nav_convert"))
        self.navigationInterface.widget(self.extract_interface.objectName()).setText(i18n.get("nav_extract"))
        self.navigationInterface.widget(self.task_interface.objectName()).setText(i18n.get("nav_task"))
        self.navigationInterface.widget(self.setting_interface.objectName()).setText(i18n.get("nav_settings"))
        self.navigationInterface.widget(self.about_interface.objectName()).setText(i18n.get("nav_about"))

    def initNavigation(self):
        from src.core.i18n import i18n
        self.addSubInterface(self.home_interface, FIF.HOME, i18n.get("nav_home"))
        self.addSubInterface(self.pack_interface, FIF.ZIP_FOLDER, i18n.get("nav_pack"))
        self.addSubInterface(self.convert_interface, FIF.SYNC, i18n.get("nav_convert"))
        self.addSubInterface(self.extract_interface, FIF.DOWNLOAD, i18n.get("nav_extract"))
        self.addSubInterface(self.task_interface, FIF.LABEL, i18n.get("nav_task"))
        
        self.addSubInterface(
            self.setting_interface, FIF.SETTING, i18n.get("nav_settings"), NavigationItemPosition.BOTTOM)
        self.addSubInterface(
            self.about_interface, FIF.INFO, i18n.get("nav_about"), NavigationItemPosition.BOTTOM)
            
        self.navigationInterface.setAcrylicEnabled(True)

    def initWindow(self):
        import os
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        icon_path = os.path.join(base_path, "src", "assets", "icon.ico")
        self.setWindowIcon(QIcon(icon_path))

def run_gui():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setOrganizationName("ComicUtilsTeam")
    app.setApplicationName("ComicUtils")
    
    from qfluentwidgets import qconfig, Theme, setTheme
    # Set default theme mode to AUTO (follow Windows system theme)
    qconfig.themeMode.defaultValue = Theme.AUTO
    qconfig.load()
    
    # Apply theme globally to QApplication
    setTheme(qconfig.theme)
    
    # Initialize i18n
    from src.core.i18n import i18n
    i18n.set_lang(cfg.language.value)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
