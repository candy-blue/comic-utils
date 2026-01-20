import sys
import os
from pathlib import Path
import subprocess

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QFileDialog,
    QMessageBox, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from src.core.archive_manager import ArchiveManager
from src.core.i18n import i18n

class ExtractWorker(QObject):
    # done, total, ok, fail
    progress_update = pyqtSignal(int, int, int, int)
    # row_idx, status_text
    item_status = pyqtSignal(int, str)
    # ok_count, fail_count, last_error
    finished = pyqtSignal(int, int, str)

    def __init__(self, items, out_dir):
        super().__init__()
        self.items = items
        self.out_dir = Path(out_dir)
        self.running = True

    def run(self):
        ok = 0
        fail = 0
        last_error = ""
        total = len(self.items)

        for idx, (path_str, _) in enumerate(self.items):
            if not self.running:
                break
            
            p = Path(path_str)
            self.item_status.emit(idx, i18n.get('status_extracting'))

            try:
                # Create a subfolder for each archive
                archive_name = p.stem
                target_dir = self.out_dir / archive_name
                
                # Ensure ArchiveManager.extract_archive is thread-safe or doesn't touch UI
                count = ArchiveManager.extract_archive(p, target_dir)
                
                if count > 0:
                    ok += 1
                    self.item_status.emit(idx, i18n.get('status_success'))
                else:
                    fail += 1
                    last_error = "No images extracted"
                    self.item_status.emit(idx, i18n.get('status_failed'))
            except Exception as e:
                fail += 1
                last_error = str(e)
                self.item_status.emit(idx, i18n.get('status_failed'))
            
            self.progress_update.emit(idx + 1, total, ok, fail)

        self.finished.emit(ok, fail, last_error)

    def stop(self):
        self.running = False

class ExtractTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.output_dir = str(Path.cwd())
        self.is_working = False
        
        self.init_ui()
        
        i18n.add_listener(self.update_texts)
        self.update_texts()
        
        # Enable Drag and Drop
        self.setAcceptDrops(True)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Top Bar: Output Directory
        top_layout = QHBoxLayout()
        self.lbl_output = QLabel() # text set in update_texts
        self.entry_output = QLineEdit(self.output_dir)
        self.entry_output.setReadOnly(True)
        self.btn_browse = QPushButton()
        self.btn_browse.clicked.connect(self.choose_output)
        self.btn_open = QPushButton()
        self.btn_open.clicked.connect(self.open_output_dir)
        
        top_layout.addWidget(self.lbl_output)
        top_layout.addWidget(self.entry_output)
        top_layout.addWidget(self.btn_browse)
        top_layout.addWidget(self.btn_open)
        layout.addLayout(top_layout)

        # Middle Area: Table and Buttons
        mid_layout = QHBoxLayout()
        
        # File Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 80)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 120)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        mid_layout.addWidget(self.table)

        # Right Buttons
        btn_layout = QVBoxLayout()
        self.btn_add = QPushButton()
        self.btn_add.clicked.connect(self.add_files)
        self.btn_remove = QPushButton()
        self.btn_remove.clicked.connect(self.remove_selected)
        self.btn_clear = QPushButton()
        self.btn_clear.clicked.connect(self.clear_list)
        
        self.lbl_hint = QLabel()
        self.lbl_hint.setWordWrap(True)
        self.lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_hint.setStyleSheet("color: gray;")
        
        self.btn_start = QPushButton()
        self.btn_start.clicked.connect(self.start_extract)
        self.btn_start.setStyleSheet("font-weight: bold; padding: 8px;")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(self.lbl_hint)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(self.btn_start)
        
        mid_layout.addLayout(btn_layout)
        layout.addLayout(mid_layout)

        # Bottom Area: Progress
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status = QLabel()
        
        layout.addWidget(self.progress)
        layout.addWidget(self.lbl_status)

    def update_texts(self):
        self.lbl_output.setText(i18n.get('output_dir'))
        self.btn_browse.setText(i18n.get('browse'))
        self.btn_open.setText(i18n.get('open_output'))
        
        headers = [i18n.get('file_col'), i18n.get('type_col'), i18n.get('status_col')]
        self.table.setHorizontalHeaderLabels(headers)
        
        self.btn_add.setText(i18n.get('add_files'))
        self.btn_remove.setText(i18n.get('remove_selected'))
        self.btn_clear.setText(i18n.get('clear_list'))
        self.btn_start.setText(i18n.get('start'))
        self.lbl_hint.setText(i18n.get('drag_drop_hint'))
        
        if not self.is_working:
            self.lbl_status.setText(i18n.get('ready'))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                ext = Path(path).suffix.lower()
                if ext in ['.epub', '.mobi', '.zip', '.cbz', '.rar', '.cbr', '.pdf', '.7z', '.cb7']:
                    self.add_file_to_list(path)

    def choose_output(self):
        path = QFileDialog.getExistingDirectory(self, i18n.get('output_dir'), self.output_dir)
        if path:
            self.output_dir = path
            self.entry_output.setText(path)

    def open_output_dir(self):
        path = Path(self.output_dir).resolve()
        path.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform == "win32":
                os.startfile(str(path))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path)], check=False)
            else:
                subprocess.run(["xdg-open", str(path)], check=False)
        except Exception as e:
            QMessageBox.warning(self, i18n.get('error'), f"Cannot open directory: {e}")

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            i18n.get('add_files'), 
            "", 
            "Archives (*.epub *.mobi *.zip *.cbz *.rar *.cbr *.pdf *.7z *.cb7);;All Files (*.*)"
        )
        for p in files:
            self.add_file_to_list(p)

    def add_file_to_list(self, path):
        if self._has_path(path):
            return
        
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        ext = Path(path).suffix.lower().lstrip(".")
        
        self.table.setItem(row, 0, QTableWidgetItem(path))
        
        type_item = QTableWidgetItem(ext or "-")
        type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 1, type_item)
        
        self.table.setItem(row, 2, QTableWidgetItem(i18n.get('status_pending')))

    def _has_path(self, path):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == path:
                return True
        return False

    def remove_selected(self):
        rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)
        for row in rows:
            self.table.removeRow(row)

    def clear_list(self):
        self.table.setRowCount(0)
        self.lbl_status.setText(i18n.get('ready'))
        self.progress.setValue(0)

    def start_extract(self):
        if self.is_working:
            return
        
        count = self.table.rowCount()
        if count == 0:
            QMessageBox.warning(self, i18n.get('error'), i18n.get('msg_no_files'))
            return

        items = []
        for row in range(count):
            path_item = self.table.item(row, 0)
            status_item = self.table.item(row, 2)
            if path_item:
                items.append((path_item.text(), row))
        
        self.is_working = True
        self.set_ui_state(False)
        self.progress.setMaximum(count)
        self.progress.setValue(0)
        
        self.thread = QThread()
        self.worker = ExtractWorker(items, self.output_dir)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.item_status.connect(self.on_item_status)
        self.worker.progress_update.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()

    def on_item_status(self, idx, status):
        self.table.setItem(idx, 2, QTableWidgetItem(status))
        self.table.scrollToItem(self.table.item(idx, 0))

    def on_progress(self, done, total, ok, fail):
        self.progress.setValue(done)
        self.lbl_status.setText(i18n.get('progress_fmt', done, total, ok, fail))

    def on_finished(self, ok, fail, last_error):
        self.is_working = False
        self.set_ui_state(True)
        
        if fail == 0:
            QMessageBox.information(self, i18n.get('msg_done_title'), i18n.get('msg_done_count', ok))
        else:
            QMessageBox.warning(self, i18n.get('msg_done_title'), i18n.get('msg_done_fail', ok, fail, last_error))

    def set_ui_state(self, enabled):
        self.btn_add.setEnabled(enabled)
        self.btn_remove.setEnabled(enabled)
        self.btn_clear.setEnabled(enabled)
        self.btn_start.setEnabled(enabled)
        self.btn_browse.setEnabled(enabled)
        self.table.setEnabled(enabled)
