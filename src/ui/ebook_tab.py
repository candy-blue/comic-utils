
import threading
import sys
import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QProgressBar, QFileDialog, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from src.modules.ebook_to_cbz.converter import ConvertError, convert_ebook
from src.core.i18n import i18n

class EbookWorker(QObject):
    progress_update = pyqtSignal(int, int, int, int) # done, total, ok, fail
    item_status = pyqtSignal(int, str) # row_idx, status
    finished = pyqtSignal()
    
    def __init__(self, items, out_dir, fmt):
        super().__init__()
        self.items = items
        self.out_dir = out_dir
        self.fmt = fmt
        self.running = True

    def run(self):
        ok_count = 0
        fail_count = 0
        total = len(self.items)
        
        for idx, (path_str, _) in enumerate(self.items):
            if not self.running:
                break
                
            p = Path(path_str)
            
            # Check if source and target formats are the same
            src_ext = p.suffix.lower().lstrip('.')
            target_ext = self.fmt.lower().lstrip('.')
            
            if src_ext == target_ext:
                self.item_status.emit(idx, i18n.get('status_skipped', 'Skipped'))
                ok_count += 1 # Count as success or just ignore? User probably wants to know it's done.
                self.progress_update.emit(idx + 1, total, ok_count, fail_count)
                continue

            self.item_status.emit(idx, i18n.get('status_converting'))
            
            try:
                convert_ebook(p, self.out_dir, self.fmt)
                self.item_status.emit(idx, i18n.get('status_success'))
                ok_count += 1
            except Exception as e:
                print(f"Error converting {p}: {e}")
                self.item_status.emit(idx, i18n.get('status_failed'))
                fail_count += 1
            
            self.progress_update.emit(idx + 1, total, ok_count, fail_count)
            
        self.finished.emit()

class EbookTab(QWidget):
    def __init__(self):
        super().__init__()
        
        self.output_dir = str(Path.cwd())
        self.is_working = False
        self._job_total = 0
        
        # Enable DnD
        self.setAcceptDrops(True)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.create_widgets()
        
        # Bind i18n
        i18n.add_listener(self.update_texts)
        self.update_texts()

    def create_widgets(self):
        # Top Bar
        self.top_group = QGroupBox(i18n.get('output_dir'))
        top_layout = QHBoxLayout()
        self.top_group.setLayout(top_layout)
        
        self.entry_output = QLineEdit(self.output_dir)
        self.btn_select = QPushButton(i18n.get('browse'))
        self.btn_select.clicked.connect(self.choose_output)
        
        self.btn_open = QPushButton(i18n.get('open_output'))
        self.btn_open.clicked.connect(self.open_output_dir)
        
        top_layout.addWidget(self.entry_output)
        top_layout.addWidget(self.btn_select)
        top_layout.addWidget(self.btn_open)
        
        self.layout.addWidget(self.top_group)
        
        # Middle Area (Table + Buttons)
        mid_layout = QHBoxLayout()
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([i18n.get('file_col'), i18n.get('type_col'), i18n.get('status_col')])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        mid_layout.addWidget(self.table)
        
        # Right Buttons
        right_layout = QVBoxLayout()
        
        self.btn_add = QPushButton(i18n.get('add_files'))
        self.btn_add.clicked.connect(self.add_files)
        right_layout.addWidget(self.btn_add)
        
        self.btn_remove = QPushButton(i18n.get('remove_selected'))
        self.btn_remove.clicked.connect(self.remove_selected)
        right_layout.addWidget(self.btn_remove)
        
        self.btn_clear = QPushButton(i18n.get('clear_list'))
        self.btn_clear.clicked.connect(self.clear_list)
        right_layout.addWidget(self.btn_clear)
        
        right_layout.addSpacing(20)
        
        # Format
        self.lbl_format = QLabel(i18n.get('format_label'))
        right_layout.addWidget(self.lbl_format)
        
        self.combo_format = QComboBox()
        self.combo_format.addItems(["cbz", "zip", "pdf", "epub", "7z"])
        right_layout.addWidget(self.combo_format)
        
        right_layout.addStretch()
        
        self.lbl_hint = QLabel(i18n.get('drag_drop_hint'))
        self.lbl_hint.setWordWrap(True)
        self.lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_hint.setStyleSheet("color: #666; font-style: italic;")
        right_layout.addWidget(self.lbl_hint)
        
        self.btn_start = QPushButton(i18n.get('start'))
        self.btn_start.clicked.connect(self.start_convert)
        self.btn_start.setMinimumHeight(40)
        # Style logic handled in MainWindow
        right_layout.addWidget(self.btn_start)
        
        right_layout.addStretch()
        
        mid_layout.addLayout(right_layout)
        self.layout.addLayout(mid_layout)
        
        # Bottom Progress
        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)
        
        self.status_label = QLabel(i18n.get('ready'))
        self.layout.addWidget(self.status_label)

    def update_texts(self):
        self.top_group.setTitle(i18n.get('output_dir'))
        self.btn_select.setText(i18n.get('browse'))
        self.btn_open.setText(i18n.get('open_output'))
        
        self.table.setHorizontalHeaderLabels([i18n.get('file_col'), i18n.get('type_col'), i18n.get('status_col')])
        
        self.btn_add.setText(i18n.get('add_files'))
        self.btn_remove.setText(i18n.get('remove_selected'))
        self.btn_clear.setText(i18n.get('clear_list'))
        self.lbl_format.setText(i18n.get('format_label'))
        self.lbl_hint.setText(i18n.get('drag_drop_hint'))
        self.btn_start.setText(i18n.get('start'))
        
        if not self.is_working:
            self.status_label.setText(i18n.get('ready'))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if os.path.isfile(path):
                self.add_file_to_list(path)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            i18n.get('add_files'), 
            "", 
            "Ebooks (*.epub *.mobi *.pdf *.cbz *.cbr *.zip *.rar *.7z);;All Files (*.*)"
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
        self.table.setItem(row, 1, QTableWidgetItem(ext or "-"))
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
        self.status_label.setText(i18n.get('ready'))
        self.progress.setValue(0)

    def choose_output(self):
        path = QFileDialog.getExistingDirectory(self, i18n.get('select_output'))
        if path:
            self.entry_output.setText(path)

    def open_output_dir(self):
        out_dir = Path(self.entry_output.text()).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(str(out_dir))
            else:
                subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", str(out_dir)], check=False)
        except Exception:
            QMessageBox.warning(self, i18n.get('error'), "Cannot open output directory")

    def start_convert(self):
        if self.is_working:
            return
            
        count = self.table.rowCount()
        if count == 0:
            QMessageBox.warning(self, i18n.get('error'), i18n.get('msg_no_files'))
            return
            
        fmt = self.combo_format.currentText()
        if fmt.lower() in ['mobi', 'rar']:
            QMessageBox.warning(self, i18n.get('error'), f"Output format '{fmt}' is not supported for writing.")
            return

        out_dir = Path(self.entry_output.text()).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        self.is_working = True
        self.toggle_inputs(False)
        self.progress.setMaximum(count)
        self.progress.setValue(0)
        
        # Prepare items: (path, row_idx) - but actually worker just needs path and we can map by index
        # To avoid issues if rows change (though inputs are disabled), let's just pass data
        items = []
        for row in range(count):
            items.append((self.table.item(row, 0).text(), row))
            self.table.setItem(row, 2, QTableWidgetItem(i18n.get('status_pending')))
            
        self.worker_thread = threading.Thread(target=self._run_worker, args=(items, out_dir, fmt))
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
    def _run_worker(self, items, out_dir, fmt):
        # We need a QObject to emit signals, but we can't create QWidgets in thread
        # So we use the approach of creating a worker object in the main thread and moving it? 
        # Or just use the signals defined in this class? 
        # Actually simplest is to define a Signal carrier class or use self signals with `emit` from thread (PyQt allows emitting signals from threads)
        
        # Re-using the logic, but adapted for thread safety
        worker = EbookWorker(items, out_dir, fmt)
        worker.progress_update.connect(self._on_progress)
        worker.item_status.connect(self._on_item_status)
        worker.finished.connect(self._on_finished)
        worker.run()

    def _on_progress(self, done, total, ok, fail):
        self.progress.setValue(done)
        self.status_label.setText(i18n.get('progress_fmt', done, total, ok, fail))

    def _on_item_status(self, row, status):
        self.table.setItem(row, 2, QTableWidgetItem(status))
        self.table.scrollToItem(self.table.item(row, 0))

    def _on_finished(self):
        self.is_working = False
        self.toggle_inputs(True)
        QMessageBox.information(self, i18n.get('msg_done_title'), i18n.get('done'))

    def toggle_inputs(self, enable):
        self.btn_add.setEnabled(enable)
        self.btn_remove.setEnabled(enable)
        self.btn_clear.setEnabled(enable)
        self.btn_start.setEnabled(enable)
        self.entry_output.setEnabled(enable)
        self.btn_select.setEnabled(enable)
        self.combo_format.setEnabled(enable)
