import os
import subprocess
import sys
import threading
from pathlib import Path

from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QGridLayout,
    QButtonGroup,
)

from src.core.i18n import i18n
from src.modules.comic_folder import converter


class LogSignal(QObject):
    log_msg = pyqtSignal(str)
    progress_update = pyqtSignal(int, int, str)
    finished = pyqtSignal(dict)


class ComicFolderTab(QWidget):
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)
        self.is_working = False
        self.stop_event = threading.Event()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_widgets()

        i18n.add_listener(self.update_texts)
        self.update_texts()

        self.signals = LogSignal()
        self.signals.log_msg.connect(self._log_gui)
        self.signals.progress_update.connect(self._update_progress_gui)
        self.signals.finished.connect(self._on_finished)

    def create_widgets(self):
        # Input directory
        self.input_group = QGroupBox(i18n.get("input_dir"))
        input_layout = QHBoxLayout()
        self.input_group.setLayout(input_layout)

        self.entry_input = QLineEdit()
        self.btn_browse_input = QPushButton(i18n.get("browse"))
        self.btn_browse_input.clicked.connect(self.select_input)

        input_layout.addWidget(self.entry_input)
        input_layout.addWidget(self.btn_browse_input)
        self.layout.addWidget(self.input_group)

        # Output directory
        self.output_group = QGroupBox(i18n.get("output_dir"))
        output_layout = QHBoxLayout()
        self.output_group.setLayout(output_layout)

        self.entry_output = QLineEdit()
        self.btn_browse_output = QPushButton(i18n.get("browse"))
        self.btn_browse_output.clicked.connect(self.select_output)
        self.btn_open_output = QPushButton(i18n.get("open_output"))
        self.btn_open_output.clicked.connect(self.open_output_dir)

        output_layout.addWidget(self.entry_output)
        output_layout.addWidget(self.btn_browse_output)
        output_layout.addWidget(self.btn_open_output)
        self.layout.addWidget(self.output_group)

        # Format selection
        self.fmt_group = QGroupBox(i18n.get("format_label"))
        fmt_layout = QGridLayout()
        self.fmt_group.setLayout(fmt_layout)

        self.formats = ["cbz", "zip", "pdf", "epub", "7z"]
        self.fmt_btn_group = QButtonGroup(self)

        for idx, fmt in enumerate(self.formats):
            btn = QRadioButton(fmt.upper())
            if fmt == "cbz":
                btn.setChecked(True)
            self.fmt_btn_group.addButton(btn)
            fmt_layout.addWidget(btn, idx // 4, idx % 4)

        self.layout.addWidget(self.fmt_group)

        self.chk_process_archives = QCheckBox(i18n.get("chk_recursive"))
        self.layout.addWidget(self.chk_process_archives)

        self.lbl_hint = QLabel(i18n.get("drag_drop_hint"))
        self.lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_hint.setStyleSheet("color: #5f6b7a; font-style: italic;")
        self.layout.addWidget(self.lbl_hint)

        # Actions
        action_layout = QHBoxLayout()
        self.start_btn = QPushButton(i18n.get("start"))
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setMinimumHeight(40)

        self.stop_btn = QPushButton(i18n.get("stop"))
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setEnabled(False)

        action_layout.addWidget(self.start_btn)
        action_layout.addWidget(self.stop_btn)
        self.layout.addLayout(action_layout)

        # Progress
        progress_layout = QVBoxLayout()
        self.status_label = QLabel(i18n.get("ready"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        self.layout.addLayout(progress_layout)

        # Log area
        self.log_group = QGroupBox(i18n.get("log"))
        log_layout = QVBoxLayout()
        self.log_group.setLayout(log_layout)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        log_layout.addWidget(self.log_area)
        self.layout.addWidget(self.log_group)

    def update_texts(self):
        self.input_group.setTitle(i18n.get("input_dir"))
        self.btn_browse_input.setText(i18n.get("browse"))

        self.output_group.setTitle(i18n.get("output_dir"))
        self.btn_browse_output.setText(i18n.get("browse"))
        self.btn_open_output.setText(i18n.get("open_output"))

        self.fmt_group.setTitle(i18n.get("format_label"))
        self.chk_process_archives.setText(i18n.get("chk_recursive"))
        self.lbl_hint.setText(i18n.get("drag_drop_hint"))

        self.start_btn.setText(i18n.get("start"))
        self.stop_btn.setText(i18n.get("stop"))

        self.log_group.setTitle(i18n.get("log"))

        if not self.is_working:
            self.status_label.setText(i18n.get("ready"))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return

        path = urls[0].toLocalFile()
        if os.path.isdir(path):
            self.entry_input.setText(path)
            if not self.entry_output.text().strip():
                self.entry_output.setText(str(Path(path).parent))
            return

        if os.path.isfile(path):
            parent = str(Path(path).parent)
            self.entry_input.setText(parent)
            if not self.entry_output.text().strip():
                self.entry_output.setText(str(Path(parent).parent))

    def select_input(self):
        path = QFileDialog.getExistingDirectory(self, i18n.get("select_input"))
        if path:
            self.entry_input.setText(path)
            if not self.entry_output.text().strip():
                self.entry_output.setText(str(Path(path).parent))

    def select_output(self):
        path = QFileDialog.getExistingDirectory(self, i18n.get("select_output"))
        if path:
            self.entry_output.setText(path)

    def open_output_dir(self):
        raw_output = self.entry_output.text().strip() or self.entry_input.text().strip()
        if not raw_output:
            QMessageBox.warning(self, i18n.get("error"), i18n.get("select_output"))
            return

        output_path = Path(raw_output).expanduser().resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            if sys.platform == "win32":
                os.startfile(str(output_path))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(output_path)], check=False)
            else:
                subprocess.run(["xdg-open", str(output_path)], check=False)
        except Exception as error:
            QMessageBox.warning(self, i18n.get("error"), i18n.get("msg_open_dir_fail", error))

    def start_processing(self):
        if self.is_working:
            return

        input_dir = self.entry_input.text().strip()
        output_dir = self.entry_output.text().strip()

        selected_btn = self.fmt_btn_group.checkedButton()
        selected_formats = [selected_btn.text().lower()] if selected_btn else []
        process_archives = self.chk_process_archives.isChecked()

        if not input_dir:
            self.log(i18n.get("select_input"))
            return

        input_path = Path(input_dir)
        if not input_path.exists() or not input_path.is_dir():
            self.log(i18n.get("input_not_exist", input_dir))
            return

        if not selected_formats:
            self.log(i18n.get("format_label"))
            return

        if output_dir:
            try:
                Path(output_dir).expanduser().resolve().mkdir(parents=True, exist_ok=True)
            except Exception as error:
                self.log(f"{i18n.get('error')}: {error}")
                return

        self.log_area.clear()
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)

        self.log(
            f"{i18n.get('processing')}\n"
            f"Input: {input_dir}\n"
            f"Output: {output_dir or input_dir}\n"
            f"Formats: {', '.join(selected_formats)}\n"
            f"Process Archives: {process_archives}\n"
        )

        self.stop_event.clear()
        self.is_working = True
        self.set_ui_state(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText(i18n.get("processing"))

        worker_args = (input_dir, output_dir, selected_formats, process_archives)
        self.worker_thread = threading.Thread(target=self.run_conversion, args=worker_args, daemon=True)
        self.worker_thread.start()

    def stop_processing(self):
        if not self.is_working:
            return

        self.stop_event.set()
        self.stop_btn.setEnabled(False)
        self.status_label.setText(i18n.get("stopping"))
        self.log(i18n.get("stopping"))

    def run_conversion(self, input_dir, output_dir, formats, process_archives):
        try:
            target_output = output_dir if output_dir else None

            def progress_cb(current, total, desc):
                self.signals.progress_update.emit(current, total, desc)

            def log_cb(msg):
                self.signals.log_msg.emit(msg)

            summary = converter.process_directory(
                input_dir,
                target_output,
                formats=formats,
                process_archives=process_archives,
                progress_callback=progress_cb,
                log_callback=log_cb,
                stop_event=self.stop_event,
            )
            self.signals.finished.emit(summary)
        except Exception as error:
            self.signals.log_msg.emit(f"{i18n.get('error')}: {error}")
            self.signals.finished.emit({"total": 0, "success": 0, "failed": 1, "cancelled": False})

    def _on_finished(self, summary):
        self.is_working = False
        self.set_ui_state(True)
        self.stop_btn.setEnabled(False)

        success = summary.get("success", 0)
        failed = summary.get("failed", 0)
        total = summary.get("total", success + failed)
        cancelled = summary.get("cancelled", False)

        if cancelled:
            self.status_label.setText(i18n.get("cancelled"))
            self.log(i18n.get("msg_done_cancel", success, failed))
            QMessageBox.information(self, i18n.get("msg_done_title"), i18n.get("msg_done_cancel", success, failed))
            return

        self.status_label.setText(i18n.get("done"))
        self.log(f"{i18n.get('done')}: {success}/{total}, Failed: {failed}")

        if failed == 0:
            QMessageBox.information(self, i18n.get("msg_done_title"), i18n.get("msg_done_count", success))
        else:
            QMessageBox.warning(self, i18n.get("msg_done_title"), i18n.get("msg_done_fail", success, failed, ""))

    def _update_progress_gui(self, current, total, desc):
        safe_total = max(total, 1)
        self.progress_bar.setMaximum(safe_total)
        self.progress_bar.setValue(min(current, safe_total))
        self.status_label.setText(desc)

    def set_ui_state(self, enabled):
        self.entry_input.setEnabled(enabled)
        self.entry_output.setEnabled(enabled)
        self.btn_browse_input.setEnabled(enabled)
        self.btn_browse_output.setEnabled(enabled)
        self.btn_open_output.setEnabled(enabled)
        self.chk_process_archives.setEnabled(enabled)
        self.start_btn.setEnabled(enabled)
        for button in self.fmt_btn_group.buttons():
            button.setEnabled(enabled)

    def log(self, message):
        self._log_gui(message)

    def _log_gui(self, message):
        self.log_area.append(str(message))
