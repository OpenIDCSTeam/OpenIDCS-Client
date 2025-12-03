class IPConfig:
    def __init__(self):
        self.ip_addr: str = ""
        self.ip_mask: str = ""

    def __dict__(self):
        return {
            "ip_addr": self.ip_addr,
            "ip_mask": self.ip_mask,
        }


class NCConfig:
    def __init__(self, **kwargs):
        self.mac_addr: str = ""
        self.nic_type: str = ""
        self.ip4_addr: list[IPConfig] = []
        self.ip6_addr: list[IPConfig] = []
        self.__load__(**kwargs)

    def __dict__(self):
        return {
            "mac_addr": self.mac_addr,
            "ip4_addr": self.ip4_addr,
            "ip6_addr": self.ip6_addr,
        }

    # 加载数据 ===============================
    def __load__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


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
