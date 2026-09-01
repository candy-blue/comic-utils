from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from qfluentwidgets import (TitleLabel, BodyLabel, PrimaryPushButton, 
                             ComboBoxSettingCard, SettingCardGroup, FluentIcon, InfoBar)
from app.widgets.drop_zone import DropZoneCard
from app.widgets.file_list import FileListWidget
from src.core.i18n import i18n
from app.config.app_config import cfg

class ConvertPage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.setObjectName("ConvertPage")
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
        self.title_label = TitleLabel(i18n.get("convert_title"), self)
        self.subtitle_label = BodyLabel(i18n.get("convert_subtitle"), self)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.subtitle_label)
        self.layout.addSpacing(16)
        
        # Drop Zone
        self.drop_zone = DropZoneCard(
            i18n.get("convert_drop_text"),
            select_mode="file",
            file_filter="漫画/电子书文件 (*.cbz *.zip *.rar *.pdf *.epub *.mobi *.7z);;所有文件 (*.*)",
            parent=self
        )
        self.drop_zone.files_dropped.connect(self.on_files_dropped)
        self.layout.addWidget(self.drop_zone)
        
        # File List
        self.file_list = FileListWidget(self)
        self.layout.addWidget(self.file_list, 1)
        
        # Settings Group
        self.setting_group = SettingCardGroup(i18n.get("convert_settings_group"), self)
        
        self.format_card = ComboBoxSettingCard(
            cfg.convertFormat,
            FluentIcon.SYNC,
            i18n.get("convert_format_title"),
            i18n.get("convert_format_desc"),
            texts=["CBZ", "ZIP", "PDF", "EPUB", "7Z"],
            parent=self.setting_group
        )
        self.setting_group.addSettingCard(self.format_card)
        self.layout.addWidget(self.setting_group)
        
        # Actions
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self.start_btn = PrimaryPushButton(FluentIcon.PLAY, i18n.get("btn_start_convert"), self)
        self.start_btn.clicked.connect(self.start_converting)
        action_layout.addWidget(self.start_btn)
        self.layout.addLayout(action_layout)

    def retranslate(self):
        self.title_label.setText(i18n.get("convert_title"))
        self.subtitle_label.setText(i18n.get("convert_subtitle"))
        self.drop_zone.label.setText(i18n.get("convert_drop_text"))
        self.setting_group.titleLabel.setText(i18n.get("convert_settings_group"))
        self.format_card.setTitle(i18n.get("convert_format_title"))
        self.format_card.setContent(i18n.get("convert_format_desc"))
        self.start_btn.setText(i18n.get("btn_start_convert"))
        
    def on_files_dropped(self, paths):
        self.file_list.add_files(paths)
        
    def start_converting(self):
        files = self.file_list.get_files()
        if not files:
            InfoBar.warning("提示", "请先添加要转换的文件", parent=self, duration=2000)
            return
            
        fmt = self.format_card.comboBox.currentText().lower()
        
        from app.models.task import Task
        from app.workers.task_manager import TaskManager
        
        tm = TaskManager.get_instance()
        for f in files:
            task = Task("convert", f, None, fmt=fmt)
            tm.add_task(task)
            
        self.file_list.clear()
        self.main_window.switchTo(self.main_window.task_interface)
