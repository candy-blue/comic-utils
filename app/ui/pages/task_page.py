from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from qfluentwidgets import (TitleLabel, BodyLabel, ScrollArea, StateToolTip, 
                             PushButton, PrimaryPushButton, FluentIcon, InfoBar,
                             SegmentedWidget)
from app.widgets.task_card import TaskCardWidget
from app.workers.task_manager import TaskManager
from src.core.i18n import i18n

class TaskPage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.setObjectName("TaskPage")
        self.setStyleSheet(f"#{self.objectName()} {{ background-color: transparent; }}")
        self.main_window = main_window
        self.task_cards = {}
        self.current_filter = "all"
        self.is_all_paused = False
        self._setup_ui()
        
        tm = TaskManager.get_instance()
        tm.task_added.connect(self.on_task_added)
        tm.task_updated.connect(self.on_task_updated)
        tm.task_removed.connect(self.on_task_removed)
        tm.tasks_cleared.connect(self.on_tasks_cleared)

        i18n.add_listener(self.retranslate)
        self.retranslate()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(20)

        # Header with Title & Top Buttons
        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)

        self.title_label = TitleLabel(i18n.get("task_title"), self)
        self.subtitle_label = BodyLabel(i18n.get("task_subtitle"), self)
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Action Buttons
        self.pause_all_btn = PushButton(FluentIcon.PAUSE, i18n.get("btn_pause_all"), self)
        self.pause_all_btn.clicked.connect(self.toggle_pause_all)
        header_layout.addWidget(self.pause_all_btn)

        self.clear_finished_btn = PushButton(FluentIcon.DELETE, i18n.get("btn_clear_finished"), self)
        self.clear_finished_btn.clicked.connect(self.clear_finished_tasks)
        header_layout.addWidget(self.clear_finished_btn)

        self.clear_all_btn = PushButton(FluentIcon.CANCEL, i18n.get("btn_clear_all"), self)
        self.clear_all_btn.clicked.connect(self.clear_all_tasks)
        header_layout.addWidget(self.clear_all_btn)

        self.layout.addLayout(header_layout)

        # Task Type Filter Tabs (SegmentedWidget)
        self.pivot = SegmentedWidget(self)
        self.pivot.addItem("all", i18n.get("task_tab_all"))
        self.pivot.addItem("pack", i18n.get("task_tab_pack"))
        self.pivot.addItem("convert", i18n.get("task_tab_convert"))
        self.pivot.addItem("extract", i18n.get("task_tab_extract"))
        self.pivot.setCurrentItem("all")
        self.pivot.currentItemChanged.connect(self._on_tab_changed)
        self.layout.addWidget(self.pivot)
        
        # Scroll Area for tasks
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)
        self.content_layout.setAlignment(Qt.AlignTop)
        
        # Empty state
        self.empty_label = BodyLabel(i18n.get("task_empty_all"), self)
        self.empty_label.setAlignment(Qt.AlignCenter)
        from qfluentwidgets import setFont
        setFont(self.empty_label, 14)
        self.empty_label.setContentsMargins(0, 40, 0, 0)
        self.content_layout.addWidget(self.empty_label)
        
        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)

    def retranslate(self):
        self.title_label.setText(i18n.get("task_title"))
        self.subtitle_label.setText(i18n.get("task_subtitle"))
        self.pause_all_btn.setText(i18n.get("btn_resume_all") if self.is_all_paused else i18n.get("btn_pause_all"))
        self.clear_finished_btn.setText(i18n.get("btn_clear_finished"))
        self.clear_all_btn.setText(i18n.get("btn_clear_all"))
        if "all" in self.pivot.items:
            self.pivot.items["all"].setText(i18n.get("task_tab_all"))
        if "pack" in self.pivot.items:
            self.pivot.items["pack"].setText(i18n.get("task_tab_pack"))
        if "convert" in self.pivot.items:
            self.pivot.items["convert"].setText(i18n.get("task_tab_convert"))
        if "extract" in self.pivot.items:
            self.pivot.items["extract"].setText(i18n.get("task_tab_extract"))
        self._apply_filter()
        for card in self.task_cards.values():
            card.update_ui()

    def _on_tab_changed(self, route_key):
        self.current_filter = route_key
        self._apply_filter()

    def _apply_filter(self):
        visible_count = 0
        for task_id, card in self.task_cards.items():
            if self.current_filter == "all" or card.task.operation == self.current_filter:
                card.show()
                visible_count += 1
            else:
                card.hide()

        if visible_count == 0 and len(self.task_cards) > 0:
            self.empty_label.setText(i18n.get("task_empty_category"))
            self.empty_label.show()
        elif len(self.task_cards) == 0:
            self.empty_label.setText(i18n.get("task_empty_all"))
            self.empty_label.show()
        else:
            self.empty_label.hide()
        
    def on_task_added(self, task):
        self.empty_label.hide()
        card = TaskCardWidget(task, self)
        self.task_cards[task.id] = card
        self.content_layout.insertWidget(0, card)
        self._apply_filter()
        
    def on_task_updated(self, task):
        if task.id in self.task_cards:
            self.task_cards[task.id].update_ui()

    def on_task_removed(self, task_id):
        if task_id in self.task_cards:
            card = self.task_cards.pop(task_id)
            self.content_layout.removeWidget(card)
            card.deleteLater()
        self._apply_filter()

    def on_tasks_cleared(self):
        for card in self.task_cards.values():
            self.content_layout.removeWidget(card)
            card.deleteLater()
        self.task_cards.clear()
        self.is_all_paused = False
        self.pause_all_btn.setText(i18n.get("btn_pause_all"))
        self.pause_all_btn.setIcon(FluentIcon.PAUSE)
        self._apply_filter()

    def toggle_pause_all(self):
        tm = TaskManager.get_instance()
        if not self.is_all_paused:
            tm.pause_all()
            self.is_all_paused = True
            self.pause_all_btn.setText(i18n.get("btn_resume_all"))
            self.pause_all_btn.setIcon(FluentIcon.PLAY)
            InfoBar.info("提示", "已暂停所有正在排队和执行的任务", duration=2000, parent=self.window())
        else:
            tm.resume_all()
            self.is_all_paused = False
            self.pause_all_btn.setText(i18n.get("btn_pause_all"))
            self.pause_all_btn.setIcon(FluentIcon.PAUSE)
            InfoBar.success("提示", "已恢复所有任务执行", duration=2000, parent=self.window())

    def clear_finished_tasks(self):
        tm = TaskManager.get_instance()
        count = tm.clear_finished_tasks()
        if count > 0:
            InfoBar.success("提示", f"已清除 {count} 个已结束任务", duration=2000, parent=self.window())
        else:
            InfoBar.info("提示", "当前没有可清除的已完成任务", duration=2000, parent=self.window())

    def clear_all_tasks(self):
        tm = TaskManager.get_instance()
        tm.clear_all_tasks()
        InfoBar.success("提示", "已清空所有任务记录", duration=2000, parent=self.window())
