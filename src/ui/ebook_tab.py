import os
import subprocess
import sys
import threading
from pathlib import Path

from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from src.core.i18n import i18n
from src.modules.ebook_to_cbz.converter import convert_ebook

SUPPORTED_INPUT_EXTS = {".epub", ".mobi", ".pdf", ".cbz", ".cbr", ".zip", ".rar", ".7z", ".cb7"}


class EbookWorker(QObject):
    progress_update = pyqtSignal(int, int, int, int)  # done, total, ok, fail
    item_status = pyqtSignal(int, str)  # row_idx, status
    finished = pyqtSignal(int, int, bool, str)  # ok, fail, cancelled, last_error

    def __init__(self, items, out_dir, fmt, stop_event):
        super().__init__()
        self.items = items
        self.out_dir = Path(out_dir)
        self.fmt = fmt
        self.stop_event = stop_event

    def run(self):
        ok_count = 0
        fail_count = 0
        processed = 0
        total = len(self.items)
        cancelled = False
        last_error = ""

        for row_idx, path_str in self.items:
            if self.stop_event.is_set():
                cancelled = True
                break

            p = Path(path_str)
            src_ext = p.suffix.lower().lstrip(".")
            target_ext = self.fmt.lower().lstrip(".")

            if not p.exists():
                fail_count += 1
                last_error = f"File not found: {p}"
                self.item_status.emit(row_idx, i18n.get("status_failed"))
                processed += 1
                self.progress_update.emit(processed, total, ok_count, fail_count)
                continue

            if src_ext == target_ext:
                ok_count += 1
                self.item_status.emit(row_idx, i18n.get("status_skipped"))
                processed += 1
                self.progress_update.emit(processed, total, ok_count, fail_count)
                continue

            self.item_status.emit(row_idx, i18n.get("status_converting"))
            try:
                convert_ebook(p, self.out_dir, self.fmt)
                ok_count += 1
                self.item_status.emit(row_idx, i18n.get("status_success"))
            except Exception as error:
                fail_count += 1
                last_error = str(error)
                self.item_status.emit(row_idx, i18n.get("status_failed"))

            processed += 1
            self.progress_update.emit(processed, total, ok_count, fail_count)

        self.finished.emit(ok_count, fail_count, cancelled, last_error)


class EbookTab(QWidget):
    def __init__(self):
        super().__init__()

        self.output_dir = str(Path.cwd())
        self.is_working = False
        self.stop_event = threading.Event()

        self.worker_thread = None
        self.worker = None

        self.setAcceptDrops(True)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_widgets()

        i18n.add_listener(self.update_texts)
        self.update_texts()

    def create_widgets(self):
        # Top bar
        self.top_group = QGroupBox(i18n.get("output_dir"))
        top_layout = QHBoxLayout()
        self.top_group.setLayout(top_layout)

        self.entry_output = QLineEdit(self.output_dir)
        self.btn_select = QPushButton(i18n.get("browse"))
        self.btn_select.clicked.connect(self.choose_output)

        self.btn_open = QPushButton(i18n.get("open_output"))
        self.btn_open.clicked.connect(self.open_output_dir)

        top_layout.addWidget(self.entry_output)
        top_layout.addWidget(self.btn_select)
        top_layout.addWidget(self.btn_open)
        self.layout.addWidget(self.top_group)

        # Middle area
        mid_layout = QHBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([i18n.get("file_col"), i18n.get("type_col"), i18n.get("status_col")])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        mid_layout.addWidget(self.table)

        right_layout = QVBoxLayout()

        self.btn_add = QPushButton(i18n.get("add_files"))
        self.btn_add.clicked.connect(self.add_files)
        right_layout.addWidget(self.btn_add)

        self.btn_remove = QPushButton(i18n.get("remove_selected"))
        self.btn_remove.clicked.connect(self.remove_selected)
        right_layout.addWidget(self.btn_remove)

        self.btn_clear = QPushButton(i18n.get("clear_list"))
        self.btn_clear.clicked.connect(self.clear_list)
        right_layout.addWidget(self.btn_clear)

        right_layout.addSpacing(20)

        self.lbl_format = QLabel(i18n.get("format_label"))
        right_layout.addWidget(self.lbl_format)

        self.combo_format = QComboBox()
        self.combo_format.addItems(["cbz", "zip", "pdf", "epub", "7z"])
        right_layout.addWidget(self.combo_format)

        right_layout.addStretch()

        self.lbl_hint = QLabel(i18n.get("drag_drop_hint"))
        self.lbl_hint.setWordWrap(True)
        self.lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_hint.setStyleSheet("color: #5f6b7a; font-style: italic;")
        right_layout.addWidget(self.lbl_hint)

        self.btn_start = QPushButton(i18n.get("start"))
        self.btn_start.clicked.connect(self.start_convert)
        self.btn_start.setMinimumHeight(40)
        right_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton(i18n.get("stop"))
        self.btn_stop.clicked.connect(self.stop_convert)
        self.btn_stop.setMinimumHeight(40)
        self.btn_stop.setEnabled(False)
        right_layout.addWidget(self.btn_stop)

        mid_layout.addLayout(right_layout)
        self.layout.addLayout(mid_layout)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.layout.addWidget(self.progress)

        self.status_label = QLabel(i18n.get("ready"))
        self.layout.addWidget(self.status_label)

    def update_texts(self):
        self.top_group.setTitle(i18n.get("output_dir"))
        self.btn_select.setText(i18n.get("browse"))
        self.btn_open.setText(i18n.get("open_output"))

        self.table.setHorizontalHeaderLabels([i18n.get("file_col"), i18n.get("type_col"), i18n.get("status_col")])

        self.btn_add.setText(i18n.get("add_files"))
        self.btn_remove.setText(i18n.get("remove_selected"))
        self.btn_clear.setText(i18n.get("clear_list"))
        self.lbl_format.setText(i18n.get("format_label"))
        self.lbl_hint.setText(i18n.get("drag_drop_hint"))
        self.btn_start.setText(i18n.get("start"))
        self.btn_stop.setText(i18n.get("stop"))

        if not self.is_working:
            self.status_label.setText(i18n.get("ready"))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path) and Path(path).suffix.lower() in SUPPORTED_INPUT_EXTS:
                self.add_file_to_list(path)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            i18n.get("add_files"),
            "",
            "Ebooks (*.epub *.mobi *.pdf *.cbz *.cbr *.zip *.rar *.7z *.cb7);;All Files (*.*)",
        )
        for path in files:
            self.add_file_to_list(path)

    def add_file_to_list(self, path):
        if self._has_path(path):
            return

        if not Path(path).exists():
            return

        row = self.table.rowCount()
        self.table.insertRow(row)

        ext = Path(path).suffix.lower().lstrip(".")
        ext_item = QTableWidgetItem(ext or "-")
        ext_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table.setItem(row, 0, QTableWidgetItem(path))
        self.table.setItem(row, 1, ext_item)
        self.table.setItem(row, 2, QTableWidgetItem(i18n.get("status_pending")))

    def _has_path(self, path):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == path:
                return True
        return False

    def remove_selected(self):
        rows = sorted({index.row() for index in self.table.selectedIndexes()}, reverse=True)
        for row in rows:
            self.table.removeRow(row)

    def clear_list(self):
        self.table.setRowCount(0)
        self.status_label.setText(i18n.get("ready"))
        self.progress.setValue(0)

    def choose_output(self):
        path = QFileDialog.getExistingDirectory(self, i18n.get("select_output"))
        if path:
            self.entry_output.setText(path)

    def open_output_dir(self):
        out_dir = Path(self.entry_output.text().strip() or self.output_dir).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(str(out_dir))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(out_dir)], check=False)
            else:
                subprocess.run(["xdg-open", str(out_dir)], check=False)
        except Exception as error:
            QMessageBox.warning(self, i18n.get("error"), i18n.get("msg_open_dir_fail", error))

    def start_convert(self):
        if self.is_working:
            return

        row_count = self.table.rowCount()
        if row_count == 0:
            QMessageBox.warning(self, i18n.get("error"), i18n.get("msg_no_files"))
            return

        fmt = self.combo_format.currentText().lower()
        if fmt in {"mobi", "rar"}:
            QMessageBox.warning(self, i18n.get("error"), f"Output format '{fmt}' is not supported for writing.")
            return

        out_dir = Path(self.entry_output.text().strip() or self.output_dir).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        self.entry_output.setText(str(out_dir))

        items = []
        for row in range(row_count):
            path_item = self.table.item(row, 0)
            if not path_item:
                continue
            items.append((row, path_item.text()))
            self.table.setItem(row, 2, QTableWidgetItem(i18n.get("status_pending")))

        if not items:
            QMessageBox.warning(self, i18n.get("error"), i18n.get("msg_no_files"))
            return

        self.stop_event.clear()
        self.is_working = True
        self.toggle_inputs(False)
        self.btn_stop.setEnabled(True)

        self.progress.setMaximum(len(items))
        self.progress.setValue(0)
        self.status_label.setText(i18n.get("processing"))

        self.worker_thread = QThread(self)
        self.worker = EbookWorker(items, out_dir, fmt, self.stop_event)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.item_status.connect(self._on_item_status)
        self.worker.progress_update.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)

        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def stop_convert(self):
        if not self.is_working:
            return

        self.stop_event.set()
        self.btn_stop.setEnabled(False)
        self.status_label.setText(i18n.get("stopping"))

    def _on_progress(self, done, total, ok, fail):
        self.progress.setMaximum(max(total, 1))
        self.progress.setValue(min(done, max(total, 1)))
        self.status_label.setText(i18n.get("progress_fmt", done, total, ok, fail))

    def _on_item_status(self, row, status):
        self.table.setItem(row, 2, QTableWidgetItem(status))
        self.table.scrollToItem(self.table.item(row, 0))

    def _on_finished(self, ok, fail, cancelled, last_error):
        self.is_working = False
        self.toggle_inputs(True)
        self.btn_stop.setEnabled(False)

        if cancelled:
            self.status_label.setText(i18n.get("cancelled"))
            QMessageBox.information(self, i18n.get("msg_done_title"), i18n.get("msg_done_cancel", ok, fail))
        elif fail == 0:
            self.status_label.setText(i18n.get("done"))
            QMessageBox.information(self, i18n.get("msg_done_title"), i18n.get("msg_done_count", ok))
        else:
            self.status_label.setText(i18n.get("error"))
            QMessageBox.warning(self, i18n.get("msg_done_title"), i18n.get("msg_done_fail", ok, fail, last_error))

        self.worker = None
        self.worker_thread = None

    def toggle_inputs(self, enable):
        self.btn_add.setEnabled(enable)
        self.btn_remove.setEnabled(enable)
        self.btn_clear.setEnabled(enable)
        self.btn_start.setEnabled(enable)
        self.entry_output.setEnabled(enable)
        self.btn_select.setEnabled(enable)
        self.btn_open.setEnabled(enable)
        self.combo_format.setEnabled(enable)
        self.table.setEnabled(enable)
