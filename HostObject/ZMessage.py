import json


class ZMessage:
    def __init__(self, **kwargs):
        self.success: bool = True
        self.actions: str = ""
        self.message: str = ""
        self.results: dict = {}
        self.execute: Exception | None = None
        self.__load__(**kwargs)

    def __load__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    # 转换为字典 ============================
    def to_dict(self):
        return {
            "success": self.success,
            "actions": self.actions,
            "message": self.message,
            "results": self.results,
            "execute": str(self.execute) if self.execute else None
        }

    # 转换为字符串 ==========================
    def __str__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)
