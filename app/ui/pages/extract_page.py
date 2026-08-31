from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from PySide6.QtCore import Qt
import os
from qfluentwidgets import (TitleLabel, BodyLabel, PrimaryPushButton, PushButton,
                             SettingCardGroup, FluentIcon, InfoBar, PushSettingCard)
from app.widgets.drop_zone import DropZoneCard
from app.widgets.file_list import FileListWidget
from src.core.i18n import i18n

class ExtractPage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.setObjectName("ExtractPage")
        self.setStyleSheet(f"#{self.objectName()} {{ background-color: transparent; }}")
        self.main_window = main_window
        self.out_dir = None
        self._setup_ui()
        i18n.add_listener(self.retranslate)
        self.retranslate()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(24)

        # Header
        self.title_label = TitleLabel(i18n.get("extract_title"), self)
        self.subtitle_label = BodyLabel(i18n.get("extract_subtitle"), self)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.subtitle_label)
        self.layout.addSpacing(16)
        
        # Drop Zone
        self.drop_zone = DropZoneCard(
            i18n.get("extract_drop_text"),
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
        self.setting_group = SettingCardGroup(i18n.get("extract_settings_group"), self)
        
        self.out_card = PushSettingCard(
            i18n.get("btn_choose_dir"),
            FluentIcon.FOLDER,
            i18n.get("extract_out_title"),
            i18n.get("extract_out_desc"),
            self.setting_group
        )
        self.out_card.clicked.connect(self.browse_output)
        self.setting_group.addSettingCard(self.out_card)
        self.layout.addWidget(self.setting_group)
        
        # Actions
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self.start_btn = PrimaryPushButton(FluentIcon.PLAY, i18n.get("btn_start_extract"), self)
        self.start_btn.clicked.connect(self.start_extracting)
        action_layout.addWidget(self.start_btn)
        self.layout.addLayout(action_layout)

    def retranslate(self):
        self.title_label.setText(i18n.get("extract_title"))
        self.subtitle_label.setText(i18n.get("extract_subtitle"))
        self.drop_zone.label.setText(i18n.get("extract_drop_text"))
        self.setting_group.titleLabel.setText(i18n.get("extract_settings_group"))
        self.out_card.setTitle(i18n.get("extract_out_title"))
        if not self.out_dir:
            self.out_card.setContent(i18n.get("extract_out_desc"))
        self.out_card.button.setText(i18n.get("btn_choose_dir"))
        self.start_btn.setText(i18n.get("btn_start_extract"))
        
    def on_files_dropped(self, paths):
        files = [p for p in paths if os.path.isfile(p)]
        if files:
            self.file_list.add_files(files)
        else:
            InfoBar.warning("提示", "请拖入文件进行提取", parent=self, duration=2000)
            
    def browse_output(self):
        dir_path = QFileDialog.getExistingDirectory(self, i18n.get("btn_choose_dir"))
        if dir_path:
            self.out_dir = dir_path
            self.out_card.setContent(dir_path)
        
    def start_extracting(self):
        files = self.file_list.get_files()
        if not files:
            InfoBar.warning("提示", "请先添加要提取的文件", parent=self, duration=2000)
            return
            
        from app.models.task import Task
        from app.workers.task_manager import TaskManager
        
        tm = TaskManager.get_instance()
        for f in files:
            task = Task("extract", f, self.out_dir, out_dir=self.out_dir)
            tm.add_task(task)
            
        self.file_list.clear()
        self.main_window.switchTo(self.main_window.task_interface)
