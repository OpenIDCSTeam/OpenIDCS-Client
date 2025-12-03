import json


class HSConfig:
    def __init__(self, **kwargs):
        self.server_type: str = ""  # 服务器类型
        self.server_addr: str = ""  # 服务器地址
        self.server_user: str = ""  # 服务器用户
        self.server_pass: str = ""  # 服务器密码
        self.filter_name: str = ""  # 过滤器名称
        self.images_path: str = ""  # 镜像存储池
        self.system_path: str = ""  # 系统存储池
        self.backup_path: str = ""  # 备份存储池
        self.extern_path: str = ""  # 数据存储池
        self.launch_path: str = ""  # 二进制路径
        self.network_nat: str = ""  # NAT网络NIC
        self.network_pub: str = ""  # PUB网络NIC
        self.extend_data: dict = {}  # API可选项
        # 加载传入的参数
        self.__load__(**kwargs)

    # 加载数据 =================================
    def __load__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    # 转换为字典 ===============================
    def __dict__(self):
        return {
            "server_type": self.server_type,
            "server_addr": self.server_addr,
            "server_user": self.server_user,
            "server_pass": self.server_pass,
            "filter_name": self.filter_name,
            "images_path": self.images_path,
            "system_path": self.system_path,
            "backup_path": self.backup_path,
            "extern_path": self.extern_path,
            "launch_path": self.launch_path,
        }

    # 转换为字符串 ===========================
    def __str__(self):
        return json.dumps(self.__dict__())
