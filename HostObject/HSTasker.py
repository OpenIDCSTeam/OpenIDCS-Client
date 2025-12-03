import abc

from HostObject.ZMessage import ZMessage


class HSTasker(abc.ABC):
    def __init__(self):
        self.process = {}  # 任务所需信息
        self.success: bool = False
        self.results: int = 0
        self.message: ZMessage | None = None

    # 检查任务状态 =========================
    def check_task(self):
        pass

    # 开始执行任务 =========================
    def start_task(self):
        pass

    # 停止执行任务 =========================
    def force_stop(self):
        pass
