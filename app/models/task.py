import uuid

class Task:
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_PAUSED = "paused"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    def __init__(self, operation, source, output, **kwargs):
        self.id = str(uuid.uuid4())
        self.operation = operation # 'pack', 'convert', 'extract'
        self.source = source
        self.output = output
        self.kwargs = kwargs
        
        self.name = source.name if hasattr(source, 'name') else str(source).split('\\')[-1].split('/')[-1]
        self.status = self.STATUS_PENDING
        self.progress = 0
        self.current = 0
        self.total = 0
        self.error = None

    @property
    def operation_cn(self):
        mapping = {
            "pack": "文件打包",
            "convert": "格式转换",
            "extract": "提取资源"
        }
        return mapping.get(self.operation, self.operation)
