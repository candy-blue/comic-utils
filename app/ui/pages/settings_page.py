from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from qfluentwidgets import (TitleLabel, BodyLabel, SettingCardGroup, 
                             ComboBoxSettingCard, FluentIcon,
                             qconfig, Theme, InfoBar)
from app.config.app_config import cfg
from src.core.i18n import i18n

class SettingsPage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.setObjectName("SettingsPage")
        self.setStyleSheet(f"#{self.objectName()} {{ background-color: transparent; }}")
        self.main_window = main_window
        self._setup_ui()
        i18n.add_listener(self.retranslate)
        self.retranslate()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(24)

        # Header
        self.title_label = TitleLabel(i18n.get("settings_title"), self)
        self.subtitle_label = BodyLabel(i18n.get("settings_subtitle"), self)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.subtitle_label)
        self.layout.addSpacing(16)
        
        # General Group
        self.general_group = SettingCardGroup(i18n.get("settings_group_general"), self)
        
        self.lang_card = ComboBoxSettingCard(
            cfg.language,
            FluentIcon.LANGUAGE,
            i18n.get("settings_lang_title"),
            i18n.get("settings_lang_desc"),
            texts=["简体中文", "English"],
            parent=self.general_group
        )
        cfg.language.valueChanged.connect(self._on_language_changed)
        self.general_group.addSettingCard(self.lang_card)
        self.layout.addWidget(self.general_group)

        # Appearance Group
        self.appearance_group = SettingCardGroup(i18n.get("settings_group_appearance"), self)
        
        self.theme_card = ComboBoxSettingCard(
            qconfig.themeMode,
            FluentIcon.BRUSH,
            i18n.get("settings_theme_title"),
            i18n.get("settings_theme_desc"),
            texts=["浅色 / Light", "深色 / Dark", "跟随系统 / Follow System"],
            parent=self.appearance_group
        )
        self.appearance_group.addSettingCard(self.theme_card)
        self.layout.addWidget(self.appearance_group)
        
        # Processing Group
        self.processing_group = SettingCardGroup(i18n.get("settings_group_processing"), self)
        
        self.concurrent_card = ComboBoxSettingCard(
            cfg.concurrentTasks,
            FluentIcon.SPEED_HIGH,
            i18n.get("settings_concurrent_title"),
            i18n.get("settings_concurrent_desc"),
            texts=["1", "2", "3", "4"],
            parent=self.processing_group
        )
        self.processing_group.addSettingCard(self.concurrent_card)
        self.layout.addWidget(self.processing_group)
        
        self.layout.addStretch()

    def _on_language_changed(self, value):
        lang = str(value)
        i18n.set_lang(lang)
        if lang == "en":
            InfoBar.success("Language Changed", "Language set to English.", duration=2500, parent=self.window())
        else:
            InfoBar.success("语言已切换", "语言已设置为简体中文。", duration=2500, parent=self.window())

    def retranslate(self):
        self.title_label.setText(i18n.get("settings_title"))
        self.subtitle_label.setText(i18n.get("settings_subtitle"))
        
        self.general_group.titleLabel.setText(i18n.get("settings_group_general"))
        self.lang_card.setTitle(i18n.get("settings_lang_title"))
        self.lang_card.setContent(i18n.get("settings_lang_desc"))

        self.appearance_group.titleLabel.setText(i18n.get("settings_group_appearance"))
        self.theme_card.setTitle(i18n.get("settings_theme_title"))
        self.theme_card.setContent(i18n.get("settings_theme_desc"))

        self.processing_group.titleLabel.setText(i18n.get("settings_group_processing"))
        self.concurrent_card.setTitle(i18n.get("settings_concurrent_title"))
        self.concurrent_card.setContent(i18n.get("settings_concurrent_desc"))
