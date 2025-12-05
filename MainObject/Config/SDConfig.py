class SDConfig:
    def __init__(self, **kwargs):
        self.hdd_name: str = ""
        self.hdd_size: int = 0
        self.__load__(**kwargs)

    def __dict__(self):
        return {
            "hdd_name": self.hdd_name,
            "hdd_size": self.hdd_size,
        }

    # 加载数据 ===============================
    def __load__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
