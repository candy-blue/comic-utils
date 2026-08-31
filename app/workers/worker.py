from PySide6.QtCore import QObject, Signal, Slot
import threading
from pathlib import Path
from src.core.archive_manager import ArchiveManager
from src.modules.comic_folder.converter import build_output_path

class ConvertWorker(QObject):
    progress = Signal(str, int, int, int) # task_id, current, total, percent
    status = Signal(str, str) # task_id, status
    finished = Signal(str, str) # task_id, final_status (completed/failed/cancelled)
    error = Signal(str, str) # task_id, error_msg

    def __init__(self, task):
        super().__init__()
        self.task = task
        self._stop_event = threading.Event()

    @Slot()
    def run(self):
        self.status.emit(self.task.id, self.task.STATUS_RUNNING)
        try:
            if self.task.operation == "pack":
                self._do_pack()
            elif self.task.operation == "convert":
                self._do_convert()
            elif self.task.operation == "extract":
                self._do_extract()
                
            if not self._stop_event.is_set():
                self.progress.emit(self.task.id, 100, 100, 100)
                self.finished.emit(self.task.id, self.task.STATUS_COMPLETED)
            else:
                self.finished.emit(self.task.id, self.task.STATUS_CANCELLED)
        except Exception as e:
            self.error.emit(self.task.id, str(e))
            self.finished.emit(self.task.id, self.task.STATUS_FAILED)

    def cancel(self):
        self._stop_event.set()

    def _do_pack(self):
        source = Path(self.task.source)
        fmt = self.task.kwargs.get('fmt', 'cbz')
        out_dir = self.task.kwargs.get('out_dir')
        
        # This is a very simplified integration. We use core ArchiveManager directly.
        # In a real scenario we'd use the full process_directory or pass a callback.
        out_path = build_output_path(source, source, out_dir, fmt, False)
        ArchiveManager.create_archive(source, out_path, fmt)

    def _do_convert(self):
        source = Path(self.task.source)
        fmt = self.task.kwargs.get('fmt', 'cbz')
        out_dir = self.task.kwargs.get('out_dir')
        
        # Temporarily extract to folder, then pack
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            ArchiveManager.extract_archive(source, tmp_path)
            
            if self._stop_event.is_set(): return
            
            out_path = build_output_path(source, source.parent, out_dir, fmt, True)
            # Avoid overwriting
            if out_path.resolve() == source.resolve():
                out_path = source.parent / f"{source.stem}_converted.{fmt}"
                
            ArchiveManager.create_archive(tmp_path, out_path, fmt)

    def _do_extract(self):
        source = Path(self.task.source)
        out_dir = self.task.kwargs.get('out_dir')
        if not out_dir:
            out_dir = source.parent / source.stem
        else:
            out_dir = Path(out_dir) / source.stem
            
        ArchiveManager.extract_archive(source, out_dir)
