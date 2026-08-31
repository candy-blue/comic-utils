from PySide6.QtWidgets import QVBoxLayout, QLabel, QFileDialog
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from qfluentwidgets import SimpleCardWidget, FluentIcon, IconWidget, BodyLabel, themeColor

class DropZoneCard(SimpleCardWidget):
    files_dropped = Signal(list)
    clicked = Signal()

    def __init__(self, text="将文件拖到这里或点击选择", select_mode="folder", file_filter="All Files (*.*)", parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.select_mode = select_mode  # "folder", "file"
        self.file_filter = file_filter
        self.setMinimumHeight(160)
        
        self.is_drag_over = False
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setAlignment(Qt.AlignCenter)
        
        self.icon_widget = IconWidget(FluentIcon.ADD, self)
        self.icon_widget.setFixedSize(32, 32)
        
        self.label = BodyLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        
        self.layout.addStretch()
        self.layout.addWidget(self.icon_widget, 0, Qt.AlignCenter)
        self.layout.addSpacing(16)
        self.layout.addWidget(self.label, 0, Qt.AlignCenter)
        self.layout.addStretch()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self._trigger_file_dialog()

    def _trigger_file_dialog(self):
        if self.select_mode == "folder":
            folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
            if folder:
                self.files_dropped.emit([folder])
        elif self.select_mode == "file":
            files, _ = QFileDialog.getOpenFileNames(self, "选择文件", "", self.file_filter)
            if files:
                self.files_dropped.emit(files)
        self.clicked.emit()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.is_drag_over = True
            self.update()

    def dragLeaveEvent(self, event):
        self.is_drag_over = False
        self.update()

    def dropEvent(self, event):
        self.is_drag_over = False
        self.update()
        
        paths = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                paths.append(url.toLocalFile())
                
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_drag_over:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            rect = self.rect().adjusted(2, 2, -2, -2)
            pen = QPen(themeColor(), 2, Qt.DashLine)
            painter.setPen(pen)
            
            c = QColor(themeColor())
            c.setAlpha(20)
            painter.setBrush(QBrush(c))
            painter.drawRoundedRect(rect, 8, 8)
