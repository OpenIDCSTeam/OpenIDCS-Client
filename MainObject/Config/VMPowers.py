import enum


class VMPowers(enum.Enum):
    # 基本状态 ==========
    STOPPED = 0x0  # 停止
    STARTED = 0x1  # 启动
    SUSPEND = 0x2  # 暂停
    # 进行状态 ==========
    ON_STOP = 0x3  # 停止
    ON_OPEN = 0x4  # 打开
    ON_SAVE = 0x5  # 保存
    ON_WAKE = 0x6  # 唤醒
    # 命令状态 ==========
    S_START = 0x7  # 打开
    S_RESET = 0x8  # 重置
    H_RESET = 0x8  # 重置
    S_CLOSE = 0x9  # 关闭
    H_CLOSE = 0xa  # 关闭
    A_PAUSE = 0xb  # 暂停
    A_WAKED = 0xc  # 唤醒
    # 其他状态 ==========
    CRASHED = 0xe  # 崩溃
    UNKNOWN = 0xf  # 未知

    def __str__(self):
        return self.name

    @staticmethod
    def to_json(value):
        """将枚举值转换为 JSON 格式"""
        if isinstance(value, VMPowers):
            return value.name
        elif isinstance(value, str):
            return value
        else:
            raise TypeError("Value must be an instance of VMPowers or a string")

    @staticmethod
    def from_json(json_value):
        """从 JSON 格式还原为枚举值"""
        if isinstance(json_value, str):
            return VMPowers[json_value]
        else:
            raise TypeError("JSON value must be a string")