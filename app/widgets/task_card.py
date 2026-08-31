from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from qfluentwidgets import (SimpleCardWidget, BodyLabel, StrongBodyLabel, 
                             CaptionLabel, TransparentToolButton, 
                             FluentIcon, ProgressBar, IconWidget)
from app.workers.task_manager import TaskManager

class TaskCardWidget(SimpleCardWidget):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setFixedHeight(88)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 12, 16, 12)
        self.layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Type Badge & Name
        self.type_badge = CaptionLabel(f"【{self.task.operation_cn}】", self)
        self.name_label = StrongBodyLabel(self.task.name, self)
        
        self.status_label = BodyLabel(self)
        
        header_layout.addWidget(self.type_badge)
        header_layout.addWidget(self.name_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        
        self.layout.addLayout(header_layout)
        
        # Progress and Actions
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        self.detail_label = CaptionLabel(self.task.operation_cn, self)
        
        self.progress_bar = ProgressBar(self)
        self.progress_bar.setMinimumHeight(4)
        
        # Pause / Resume Button
        self.pause_btn = TransparentToolButton(FluentIcon.PAUSE, self)
        self.pause_btn.setFixedSize(28, 28)
        self.pause_btn.setToolTip("暂停任务")
        self.pause_btn.clicked.connect(self._on_toggle_pause)
        
        # Delete / Remove Button
        self.delete_btn = TransparentToolButton(FluentIcon.DELETE, self)
        self.delete_btn.setFixedSize(28, 28)
        self.delete_btn.setToolTip("删除任务")
        self.delete_btn.clicked.connect(self._on_delete)
        
        bottom_layout.addWidget(self.detail_label)
        bottom_layout.addSpacing(12)
        bottom_layout.addWidget(self.progress_bar, 1)
        bottom_layout.addSpacing(12)
        bottom_layout.addWidget(self.pause_btn)
        bottom_layout.addWidget(self.delete_btn)
        
        self.layout.addLayout(bottom_layout)
        
        self.update_ui()
        
    def _on_toggle_pause(self):
        tm = TaskManager.get_instance()
        if self.task.status == self.task.STATUS_PAUSED:
            tm.resume_task(self.task.id)
        else:
            tm.pause_task(self.task.id)

    def _on_delete(self):
        TaskManager.get_instance().delete_task(self.task.id)
        
    def update_ui(self):
        self.type_badge.setText(f"【{self.task.operation_cn}】")
        
        if self.task.status == self.task.STATUS_PENDING:
            self.status_label.setText("⏳ 等待中")
            self.status_label.setStyleSheet("")
            self.progress_bar.setValue(0)
            self.pause_btn.setIcon(FluentIcon.PAUSE)
            self.pause_btn.setToolTip("暂停任务")
            self.pause_btn.show()
            
        elif self.task.status == self.task.STATUS_RUNNING:
            self.status_label.setText("⟳ 处理中")
            self.status_label.setStyleSheet("")
            if self.task.progress > 0:
                self.progress_bar.setValue(self.task.progress)
            else:
                self.progress_bar.setMaximum(0) # Indeterminate
            self.pause_btn.setIcon(FluentIcon.PAUSE)
            self.pause_btn.setToolTip("暂停任务")
            self.pause_btn.show()
            
        elif self.task.status == self.task.STATUS_PAUSED:
            self.status_label.setText("⏸ 已暂停")
            self.status_label.setStyleSheet("color: #F59E0B;")
            self.pause_btn.setIcon(FluentIcon.PLAY)
            self.pause_btn.setToolTip("继续任务")
            self.pause_btn.show()
            
        elif self.task.status == self.task.STATUS_COMPLETED:
            self.status_label.setText("✓ 已完成")
            self.status_label.setStyleSheet("color: #22C55E;")
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(100)
            self.pause_btn.hide()
            
        elif self.task.status == self.task.STATUS_FAILED:
            self.status_label.setText("✕ 失败")
            self.status_label.setStyleSheet("color: #EF4444;")
            self.progress_bar.setMaximum(100)
            self.detail_label.setText(f"错误: {self.task.error or '处理异常'}")
            self.pause_btn.hide()
            
        elif self.task.status == self.task.STATUS_CANCELLED:
            self.status_label.setText("✕ 已取消")
            self.status_label.setStyleSheet("")
            self.pause_btn.hide()
