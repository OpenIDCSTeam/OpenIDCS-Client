# class IPConfig:
#     def __init__(self):
#         self.ip_addr: str = ""
#         self.ip_mask: str = ""
#
#     def __dict__(self):
#         return {
#             "ip_addr": self.ip_addr,
#             "ip_mask": self.ip_mask,
#         }


class NCConfig:
    def __init__(self, **kwargs):
        self.mac_addr: str = ""
        self.nic_type: str = ""
        self.ip4_addr: str = ""
        self.ip6_addr: str = ""
        self.__load__(**kwargs)

    def __dict__(self):
        return {
            "mac_addr": self.mac_addr,
            "nic_type": self.nic_type,
            "ip4_addr": self.ip4_addr,
            "ip6_addr": self.ip6_addr,
        }

    # 加载数据 ===============================
    def __load__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        if self.mac_addr == "":
            self.mac_addr = self.send_mac()

    # 获取MAC地址 =============================
    def send_mac(self):
        ip4_parts = self.ip4_addr.split(".")
        mac_parts = [format(int(part), '02x') for part in ip4_parts]  # 转换为两位十六进制
        mac_parts = ":".join(mac_parts)
        if self.ip4_addr.startswith("192"):
            return "00:1C:" + mac_parts
        elif self.ip4_addr.startswith("172"):
            return "CC:D9:" + mac_parts
        elif self.ip4_addr.startswith("10"):
            return "10:F6:" + mac_parts
        elif self.ip4_addr.startswith("100"):
            return "00:1E:" + mac_parts
        else:
            return "00:00:" + mac_parts

    # # #####################################################################
    # # 将IP地址转换为MAC地址的后32位
    # # :param ip: IP地址字符串，如 "192.168.1.1"
    # # :return: MAC地址后4段，如 "c0:a8:01:01"
    # # #####################################################################
    # def ip_to_mac(self, ip):
    #     ip_parts = ip.split(".")
    #     mac_parts = [format(int(part), '02x') for part in ip_parts]  # 转换为两位十六进制
    #     return ":".join(mac_parts)
    #
    # # #####################################################################
    # # 将MAC地址的后32位转换为IP地址
    # # :param mac: MAC地址字符串，如 "00:00:c0:a8:01:01"
    # # :return: IP地址，如 "192.168.1.1"
    # # #####################################################################
    # def mac_to_ip(self, mac):
    #     mac_parts = mac.split(":")
    #     ip_parts = mac_parts[-4:]  # 取MAC地址的后4个部分
    #     ip_address = ".".join(str(int(part, 16)) for part in ip_parts)  # 转换为十进制
    #     return ip_address


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
