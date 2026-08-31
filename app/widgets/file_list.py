from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, Signal
import os
from qfluentwidgets import SimpleCardWidget, BodyLabel, TransparentToolButton, FluentIcon, ScrollArea, IconWidget

class FileItemWidget(SimpleCardWidget):
    remove_clicked = Signal(str)

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.setFixedHeight(64)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        
        name = os.path.basename(path)
        if os.path.isdir(path):
            icon = FluentIcon.FOLDER
            info = "文件夹"
        else:
            icon = FluentIcon.DOCUMENT
            size = os.path.getsize(path) / (1024 * 1024)
            info = f"{size:.2f} MB"
            
        icon_widget = IconWidget(icon)
        icon_widget.setFixedSize(24, 24)
        
        from qfluentwidgets import StrongBodyLabel, CaptionLabel
        name_label = StrongBodyLabel(name, self)
        info_label = CaptionLabel(info, self)
        
        remove_btn = TransparentToolButton(FluentIcon.CLOSE, self)
        remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self.path))
        
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.addWidget(name_label)
        info_layout.addWidget(info_label)
        
        layout.addWidget(icon_widget)
        layout.addSpacing(16)
        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(remove_btn)

class FileListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.files = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.content_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
    def add_files(self, paths):
        for path in paths:
            if path not in self.files:
                self.files.append(path)
                item = FileItemWidget(path)
                item.remove_clicked.connect(self.remove_file)
                self.content_layout.addWidget(item)
                
    def remove_file(self, path):
        if path in self.files:
            self.files.remove(path)
            for i in range(self.content_layout.count()):
                item = self.content_layout.itemAt(i).widget()
                if isinstance(item, FileItemWidget) and item.path == path:
                    item.deleteLater()
                    break

    def get_files(self):
        return self.files
        
    def clear(self):
        self.files.clear()
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
