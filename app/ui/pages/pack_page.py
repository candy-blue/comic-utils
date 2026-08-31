from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
import os
from pathlib import Path
from qfluentwidgets import (TitleLabel, BodyLabel, PrimaryPushButton, 
                             ComboBoxSettingCard, SwitchSettingCard, SettingCardGroup, 
                             FluentIcon, InfoBar)
from app.widgets.drop_zone import DropZoneCard
from app.widgets.file_list import FileListWidget
from src.core.utils import is_image_file
from src.core.i18n import i18n

class PackPage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.setObjectName("PackPage")
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
        self.title_label = TitleLabel(i18n.get("pack_title"), self)
        self.subtitle_label = BodyLabel(i18n.get("pack_subtitle"), self)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.subtitle_label)
        self.layout.addSpacing(16)
        
        # Drop Zone
        self.drop_zone = DropZoneCard(
            i18n.get("pack_drop_text"),
            select_mode="folder",
            parent=self
        )
        self.drop_zone.files_dropped.connect(self.on_files_dropped)
        self.layout.addWidget(self.drop_zone)
        
        # File List
        self.file_list = FileListWidget(self)
        self.layout.addWidget(self.file_list, 1) # stretch
        
        # Settings Group
        self.setting_group = SettingCardGroup(i18n.get("pack_settings_group"), self)
        
        from app.config.app_config import cfg
        self.format_card = ComboBoxSettingCard(
            cfg.packFormat,
            FluentIcon.TILES,
            i18n.get("pack_format_title"),
            i18n.get("pack_format_desc"),
            texts=["CBZ", "ZIP", "PDF", "EPUB", "7Z"],
            parent=self.setting_group
        )
        self.setting_group.addSettingCard(self.format_card)

        # Recursive Processing Switch Card
        self.recursive_card = SwitchSettingCard(
            FluentIcon.FOLDER,
            i18n.get("pack_recursive_title"),
            i18n.get("pack_recursive_desc"),
            parent=self.setting_group
        )
        self.recursive_card.setChecked(True)
        self.setting_group.addSettingCard(self.recursive_card)

        self.layout.addWidget(self.setting_group)
        
        # Actions
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self.start_btn = PrimaryPushButton(FluentIcon.PLAY, i18n.get("btn_start_pack"), self)
        self.start_btn.clicked.connect(self.start_packing)
        action_layout.addWidget(self.start_btn)
        self.layout.addLayout(action_layout)
        
    def retranslate(self):
        self.title_label.setText(i18n.get("pack_title"))
        self.subtitle_label.setText(i18n.get("pack_subtitle"))
        self.drop_zone.label.setText(i18n.get("pack_drop_text"))
        self.setting_group.titleLabel.setText(i18n.get("pack_settings_group"))
        self.format_card.setTitle(i18n.get("pack_format_title"))
        self.format_card.setContent(i18n.get("pack_format_desc"))
        self.recursive_card.setTitle(i18n.get("pack_recursive_title"))
        self.recursive_card.setContent(i18n.get("pack_recursive_desc"))
        self.start_btn.setText(i18n.get("btn_start_pack"))

    def on_files_dropped(self, paths):
        dirs = [p for p in paths if os.path.isdir(p)]
        if dirs:
            self.file_list.add_files(dirs)
        else:
            InfoBar.warning(
                title="提示",
                content="请拖入文件夹进行打包",
                parent=self,
                duration=2000
            )
        
    def start_packing(self):
        files = self.file_list.get_files()
        if not files:
            InfoBar.warning("提示", "请先添加要打包的文件夹", parent=self, duration=2000)
            return
            
        fmt = self.format_card.comboBox.currentText().lower()
        is_recursive = self.recursive_card.isChecked()
        
        from app.models.task import Task
        from app.workers.task_manager import TaskManager
        
        tm = TaskManager.get_instance()
        tasks_to_add = []
        
        for f in files:
            f_path = Path(f)
            if is_recursive and f_path.is_dir():
                found_any = False
                for root, dirs, filenames in os.walk(f_path):
                    if any(is_image_file(file) for file in filenames):
                        tasks_to_add.append(Path(root))
                        found_any = True
                if not found_any:
                    tasks_to_add.append(f_path)
            else:
                tasks_to_add.append(f_path)

        for folder in tasks_to_add:
            task = Task("pack", folder, None, fmt=fmt)
            tm.add_task(task)
            
        self.file_list.clear()
        self.main_window.switchTo(self.main_window.task_interface)
