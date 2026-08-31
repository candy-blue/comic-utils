from PySide6.QtCore import QObject, Signal, QThread
from app.workers.worker import ConvertWorker

class TaskManager(QObject):
    task_added = Signal(object) # Task
    task_updated = Signal(object) # Task
    task_removed = Signal(str) # task_id
    tasks_cleared = Signal()
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = TaskManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.tasks = {} # id -> Task
        self.workers = {} # id -> (QThread, ConvertWorker)
        self.max_concurrent = 2
        self.running_count = 0
        self.queue = []

    def add_task(self, task):
        self.tasks[task.id] = task
        self.queue.append(task.id)
        self.task_added.emit(task)
        self._process_queue()

    def _process_queue(self):
        while self.running_count < self.max_concurrent and self.queue:
            task_id = self.queue.pop(0)
            self._start_task(self.tasks[task_id])

    def _start_task(self, task):
        thread = QThread()
        worker = ConvertWorker(task)
        worker.moveToThread(thread)
        
        # Connect signals
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        
        worker.status.connect(self._on_status)
        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_finished)
        worker.error.connect(self._on_error)
        
        self.workers[task.id] = (thread, worker)
        self.running_count += 1
        thread.start()

    def _on_status(self, task_id, status):
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            self.task_updated.emit(self.tasks[task_id])

    def _on_progress(self, task_id, current, total, percent):
        if task_id in self.tasks:
            self.tasks[task_id].current = current
            self.tasks[task_id].total = total
            self.tasks[task_id].progress = percent
            self.task_updated.emit(self.tasks[task_id])

    def _on_error(self, task_id, error_msg):
        if task_id in self.tasks:
            self.tasks[task_id].error = error_msg
            self.tasks[task_id].status = self.tasks[task_id].STATUS_FAILED
            self.task_updated.emit(self.tasks[task_id])

    def _on_finished(self, task_id, final_status):
        if task_id in self.tasks:
            self.tasks[task_id].status = final_status
            self.task_updated.emit(self.tasks[task_id])
            
        if task_id in self.workers:
            del self.workers[task_id]
            self.running_count -= 1
            self._process_queue()

    def cancel_task(self, task_id):
        if task_id in self.queue:
            self.queue.remove(task_id)
            self.tasks[task_id].status = self.tasks[task_id].STATUS_CANCELLED
            self.task_updated.emit(self.tasks[task_id])
        elif task_id in self.workers:
            _, worker = self.workers[task_id]
            worker.cancel()

    def get_all_tasks(self):
        return list(self.tasks.values())

    def pause_task(self, task_id):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task_id in self.queue:
                self.queue.remove(task_id)
            if task_id in self.workers:
                _, worker = self.workers[task_id]
                worker.cancel()
            task.status = task.STATUS_PAUSED
            self.task_updated.emit(task)

    def resume_task(self, task_id):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == task.STATUS_PAUSED:
                task.status = task.STATUS_PENDING
                self.queue.append(task_id)
                self.task_updated.emit(task)
                self._process_queue()

    def delete_task(self, task_id):
        if task_id in self.tasks:
            if task_id in self.queue:
                self.queue.remove(task_id)
            if task_id in self.workers:
                _, worker = self.workers[task_id]
                worker.cancel()
            del self.tasks[task_id]
            self.task_removed.emit(task_id)

    def pause_all(self):
        for tid, task in list(self.tasks.items()):
            if task.status in (task.STATUS_PENDING, task.STATUS_RUNNING):
                self.pause_task(tid)

    def resume_all(self):
        for tid, task in list(self.tasks.items()):
            if task.status == task.STATUS_PAUSED:
                self.resume_task(tid)

    def clear_finished_tasks(self):
        """ Clear all completed, failed, or cancelled tasks """
        finished_ids = [
            tid for tid, task in self.tasks.items()
            if task.status in (task.STATUS_COMPLETED, task.STATUS_FAILED, task.STATUS_CANCELLED)
        ]
        for tid in finished_ids:
            del self.tasks[tid]
            self.task_removed.emit(tid)
        return len(finished_ids)

    def clear_all_tasks(self):
        """ Cancel all and clear entire task list """
        for tid in list(self.queue):
            self.cancel_task(tid)
        for tid in list(self.workers.keys()):
            self.cancel_task(tid)
        self.tasks.clear()
        self.tasks_cleared.emit()
