import abc
from HostObject.HSConfig import HSConfig
from HostObject.HSTasker import HSTasker
from HostObject.VMPowers import VMPowers
from HostObject.HWStatus import HWStatus
from HostObject.ZMessage import ZMessage
from HostObject.VMConfig import VMConfig


class BaseServer(abc.ABC):
    def __init__(self, in_config: HSConfig):
        self.config: HSConfig | None = in_config
        self.status: HWStatus | None = HWStatus()
        self.record: dict[str, VMConfig] = {}
        self.logger: list[ZMessage] = []
        self.tasker: list[HSTasker] = []

    # 宿主机状态 ==========================================
    def HSStatus(self) -> HWStatus:
        pass

    # 初始宿主机 ==========================================
    def HSCreate(self) -> ZMessage:
        pass

    # 还原宿主机 ==========================================
    def HSDelete(self) -> ZMessage:
        pass

    # 配置宿主机 ==========================================
    def HSConfig(self) -> ZMessage:
        pass

    # 读取宿主机 ==========================================
    def HSLoader(self) -> ZMessage:
        pass

    # 宿主机操作 ==========================================
    def HSAction(self) -> ZMessage:
        pass

    # 虚拟机列出 ==========================================
    def VMStatus(self, uuid: str | None) -> list[HWStatus]:
        pass

    # 创建虚拟机 ==========================================
    def VMCreate(self, input_config: VMConfig) -> ZMessage:
        pass

    # 配置虚拟机 ==========================================
    def VMUpdate(self, input_config: VMConfig) -> ZMessage:
        pass

    # 删除虚拟机 ==========================================
    def VMDelete(self, uuid: str, p: VMPowers) -> ZMessage:
        pass

    # 虚拟机电源 ==========================================
    def VMPowers(self, uuid: str, p: VMPowers) -> ZMessage:
        pass
