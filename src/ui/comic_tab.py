
import os
import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QPushButton, QCheckBox, QProgressBar, QTextEdit, QFileDialog, QGridLayout,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from src.modules.comic_folder import converter
from src.core.i18n import i18n

class LogSignal(QObject):
    log_msg = pyqtSignal(str)
    progress_update = pyqtSignal(int, int, str)
    finished = pyqtSignal()

class ComicFolderTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Enable DnD
        self.setAcceptDrops(True)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.create_widgets()
        
        # Bind i18n
        i18n.add_listener(self.update_texts)
        self.update_texts()
        
        # Signals
        self.signals = LogSignal()
        self.signals.log_msg.connect(self._log_gui)
        self.signals.progress_update.connect(self._update_progress_gui)
        self.signals.finished.connect(self._on_finished)

    def create_widgets(self):
        # Input Directory
        self.input_group = QGroupBox(i18n.get('input_dir'))
        input_layout = QHBoxLayout()
        self.input_group.setLayout(input_layout)
        
        self.entry_input = QLineEdit()
        self.btn_browse_input = QPushButton(i18n.get('browse'))
        self.btn_browse_input.clicked.connect(self.select_input)
        
        input_layout.addWidget(self.entry_input)
        input_layout.addWidget(self.btn_browse_input)
        
        self.layout.addWidget(self.input_group)
        
        # Output Directory
        self.output_group = QGroupBox(i18n.get('output_dir'))
        output_layout = QHBoxLayout()
        self.output_group.setLayout(output_layout)
        
        self.entry_output = QLineEdit()
        self.btn_browse_output = QPushButton(i18n.get('browse'))
        self.btn_browse_output.clicked.connect(self.select_output)
        
        output_layout.addWidget(self.entry_output)
        output_layout.addWidget(self.btn_browse_output)
        
        self.layout.addWidget(self.output_group)
        
        # Format Selection
        self.fmt_group = QGroupBox(i18n.get('format_label'))
        fmt_layout = QGridLayout()
        self.fmt_group.setLayout(fmt_layout)
        
        self.formats = ["cbz", "zip", "pdf", "epub", "7z"]
        self.fmt_btn_group = QButtonGroup(self)
        
        for i, fmt in enumerate(self.formats):
            btn = QRadioButton(fmt.upper())
            if fmt == "cbz":
                btn.setChecked(True)
            self.fmt_btn_group.addButton(btn)
            fmt_layout.addWidget(btn, i // 4, i % 4)
        
        self.layout.addWidget(self.fmt_group)
        
        # Recursive / Process Archives option
        self.chk_process_archives = QCheckBox(i18n.get('chk_recursive'))
        self.layout.addWidget(self.chk_process_archives)
        
        # Drag Drop Hint
        self.lbl_hint = QLabel(i18n.get('drag_drop_hint'))
        self.lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_hint.setStyleSheet("color: #666; font-style: italic;")
        self.layout.addWidget(self.lbl_hint)
        
        # Start Button
        self.start_btn = QPushButton(i18n.get('start'))
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setMinimumHeight(40)
        self.layout.addWidget(self.start_btn)
        
        # Progress
        progress_layout = QVBoxLayout()
        self.status_label = QLabel(i18n.get('ready'))
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        self.layout.addLayout(progress_layout)
        
        # Log Area
        self.log_group = QGroupBox(i18n.get('log'))
        log_layout = QVBoxLayout()
        self.log_group.setLayout(log_layout)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        log_layout.addWidget(self.log_area)
        
        self.layout.addWidget(self.log_group)

    def update_texts(self):
        self.input_group.setTitle(i18n.get('input_dir'))
        self.btn_browse_input.setText(i18n.get('browse'))
        self.output_group.setTitle(i18n.get('output_dir'))
        self.btn_browse_output.setText(i18n.get('browse'))
        self.fmt_group.setTitle(i18n.get('format_label'))
        self.lbl_hint.setText(i18n.get('drag_drop_hint'))
        self.chk_process_archives.setText(i18n.get('chk_recursive'))
        self.start_btn.setText(i18n.get('start'))
        self.log_group.setTitle(i18n.get('log'))
        
        if not self.progress_bar.value():
            self.status_label.setText(i18n.get('ready'))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.entry_input.setText(path)
                if not self.entry_output.text():
                    self.entry_output.setText(os.path.dirname(path))
            else:
                self.entry_input.setText(os.path.dirname(path))
                if not self.entry_output.text():
                    self.entry_output.setText(os.path.dirname(os.path.dirname(path)))

    def select_input(self):
        path = QFileDialog.getExistingDirectory(self, i18n.get('select_input'))
        if path:
            self.entry_input.setText(path)
            if not self.entry_output.text():
                self.entry_output.setText(os.path.dirname(path))

    def select_output(self):
        path = QFileDialog.getExistingDirectory(self, i18n.get('select_output'))
        if path:
            self.entry_output.setText(path)

    def start_processing(self):
        input_dir = self.entry_input.text()
        output_dir = self.entry_output.text()
        
        selected_btn = self.fmt_btn_group.checkedButton()
        if selected_btn:
            selected_formats = [selected_btn.text().lower()]
        else:
            selected_formats = []
            
        process_archives = self.chk_process_archives.isChecked()
        
        if not input_dir:
            self.log(i18n.get('select_input'))
            return
            
        if not os.path.exists(input_dir):
            self.log(i18n.get('input_not_exist', input_dir))
            return
            
        if not selected_formats:
            self.log("Please select at least one format.")
            return

        # Disable buttons
        self.start_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_area.clear()
        self.log(f"{i18n.get('processing')}\nInput: {input_dir}\nOutput: {output_dir}\nFormats: {', '.join(selected_formats)}\nProcess Archives: {process_archives}\n")
        
        # Run in thread
        threading.Thread(target=self.run_conversion, args=(input_dir, output_dir, selected_formats, process_archives), daemon=True).start()

    def run_conversion(self, input_dir, output_dir, formats, process_archives):
        try:
            target_output = output_dir if output_dir.strip() else None
            
            # Wrapper for callbacks to emit signals
            def progress_cb(current, total, desc):
                self.signals.progress_update.emit(current, total, desc)
                
            def log_cb(msg):
                self.signals.log_msg.emit(msg)
            
            converter.process_directory(
                input_dir, 
                target_output, 
                formats=formats,
                process_archives=process_archives,
                progress_callback=progress_cb,
                log_callback=log_cb
            )
            self.signals.log_msg.emit(i18n.get('done'))
        except Exception as e:
            self.signals.log_msg.emit(f"{i18n.get('error')}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.signals.finished.emit()

    def _on_finished(self):
        self.start_btn.setEnabled(True)

    def _update_progress_gui(self, current, total, desc):
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
        self.status_label.setText(desc)

    def log(self, message):
        self._log_gui(message)
        
    def _log_gui(self, message):
        self.log_area.append(message)
