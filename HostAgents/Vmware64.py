import os
import shutil
import subprocess

from HostAgents.Template import BaseServer
from HostObject.HSConfig import HSConfig
from HostObject.VMPowers import VMPowers
from HostObject.HWStatus import HWStatus
from HostObject.ZMConfig import NCConfig
from HostObject.ZMessage import ZMessage
from HostObject.VMConfig import VMConfig
from HostAgents.VMRestHost.VRestAPI import VRestAPI


class HostServer(BaseServer):
    def __init__(self, in_config: HSConfig):
        super().__init__(in_config)
        self.vmrest_pid = None
        self.vmrest_api = VRestAPI(
            self.config.server_addr,
            self.config.server_user,
            self.config.server_pass,
        )

    # 宿主机状态 ==========================================
    def HSStatus(self) -> HWStatus:
        return HWStatus()

    # 初始宿主机 ==========================================
    def HSCreate(self) -> ZMessage:
        pass

    # 还原宿主机 ==========================================
    def HSDelete(self) -> ZMessage:
        pass

    # 读取宿主机 ==========================================
    def HSLoader(self) -> ZMessage:
        # 启动VM Rest Server
        vmrest_path = os.path.join(
            self.config.launch_path, "vmrest.exe")
        # 检查文件是否存在
        if not os.path.exists(vmrest_path):
            return ZMessage(
                success=False,
                action="HSLoader",
                message=f"vmrest.exe not found at: {vmrest_path}",
            )
        # 配置后台运行（隐藏窗口）
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        # 启动进程
        self.vmrest_pid = subprocess.Popen(
            [vmrest_path],
            cwd=self.config.launch_path,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return ZMessage(
            success=True,
            action="HSLoader",
            message="VM Rest Server loaded",
        )

    # 卸载宿主机 ==========================================
    def HSUnload(self) -> ZMessage:
        """终止vmrest.exe进程"""
        if self.vmrest_pid is None:
            return ZMessage(
                success=False,
                action="HSUnload",
                message="VM Rest Server is not running",
            )
        try:
            self.vmrest_pid.terminate()  # 尝试正常终止
            self.vmrest_pid.wait(timeout=5)  # 等待最多5秒
        except subprocess.TimeoutExpired:
            self.vmrest_pid.kill()  # 强制终止
        finally:
            self.vmrest_pid = None
        return ZMessage(
            success=True,
            action="HSUnload",
            message="VM Rest Server stopped",
        )

    # 配置宿主机 ==========================================
    def HSConfig(self) -> ZMessage:
        pass

    # 宿主机操作 ==========================================
    def HSAction(self, action: str = "status") -> ZMessage:
        pass

    # 虚拟机列出 ==========================================
    def VMStatus(self, uuid: str | None) -> list[HWStatus]:
        result_list: list[HWStatus] = []
        # 电源状态映射（VMRest API返回值 -> VMPowers枚举）
        power_map = {
            "poweredOn": VMPowers.STARTED,
            "poweredOff": VMPowers.STOPPED,
            "suspended": VMPowers.SUSPEND,
            "paused": VMPowers.SUSPEND,
        }
        all_vms = self.vmrest_api.get_all_vm()
        if not all_vms.success:
            return result_list
        vms = all_vms.results if isinstance(all_vms.results, list) else []
        for vm in vms:
            vm_path = vm.get("path", "")
            # 从路径中提取虚拟机名称 =================================
            vm_name = os.path.splitext(os.path.basename(vm_path))[0]
            # 过滤虚拟机名称 =========================================
            if self.config.filter_name:
                if not vm_name.startswith(self.config.filter_name):
                    continue
            # 获取电源状态 ===========================================
            power_result = self.vmrest_api.get_powers(vm_name)
            ac_status = VMPowers.UNKNOWN
            if power_result.success:
                power_state = power_result.results.get("power_state", "")
                ac_status = power_map.get(power_state, VMPowers.UNKNOWN)
            result_list.append(HWStatus(ac_status=ac_status))
        return result_list

    # 创建虚拟机 #################################################################
    def VMCreate(self, input_config: VMConfig) -> ZMessage:
        self.record[input_config.vm_uuid] = input_config
        # 路径处理 ===============================================================
        vm_save_path = os.path.join(self.config.system_path, input_config.vm_uuid)
        os.mkdir(vm_save_path) if not os.path.exists(vm_save_path) else None
        # VM文件名 ===============================================================
        vm_file_name = os.path.join(vm_save_path, input_config.vm_uuid)
        # VM配置 =================================================================
        vm_save_conf = self.vmrest_api.create_vmx(input_config)
        with open(os.path.join(vm_file_name + ".vmx"), "w") as vm_save_file:
            vm_save_file.write(vm_save_conf)
        # 复制镜像 ===============================================================
        im = os.path.join(self.config.images_path, input_config.os_name + ".vmdk")
        shutil.copy(im, vm_file_name + ".vmdk")
        # 注册机器 ===============================================================
        result = self.vmrest_api.loader_vmx(vm_file_name + ".vmx")
        print(result)
        # 返回结果 ===============================================================
        return ZMessage(
            success=True,
            action="VMCreate",
            message="VM created",
        )

    # 配置虚拟机 ==========================================
    def VMUpdate(self, input_config: VMConfig) -> ZMessage:
        pass

    # 删除虚拟机 ==========================================
    def VMDelete(self, uuid: str, p: VMPowers) -> ZMessage:
        pass

    # 虚拟机电源 ==========================================
    def VMPowers(self, uuid: str, p: VMPowers) -> ZMessage:
        result = self.vmrest_api.set_powers(uuid, p)
        result.actions = "VMPowers"
        if result.success:
            result.message = f"VM {uuid} power set to {p.name}"
        print(result)
        return result


# 测试代码 ========================================================================
if __name__ == "__main__":
    hs_config = HSConfig(
        server_type="Win64VMW",
        server_addr="localhost:8697",
        server_user="root",
        server_pass="VmD55!MkW@%Q",
        filter_name="ecs_",
        images_path=r"G:\OIDCS\Win64VMW\images",
        system_path=r"G:\OIDCS\Win64VMW\system",
        backup_path=r"G:\OIDCS\Win64VMW\backup",
        extern_path=r"G:\OIDCS\Win64VMW\extern",
        launch_path=r"C:\Program Files (x86)\VMware\VMware Workstation",
        network_nat="nat",
        network_pub="",
        extend_data={

        }
    )
    vm_config = VMConfig(
        vm_uuid="Tests-All",
        os_name="windows10x64",
        cpu_num=4,
        mem_num=2048,
        hdd_num=10240,
        gpu_num=0,
        net_num=100,
        flu_num=100,
        nat_num=100,
        web_num=100,
        gpu_mem=8192,
        speed_u=100,
        speed_d=100,
        nic_all={
            "ethernet0": NCConfig(
                ip4_addr="192.168.1.1",
            )
        }
    )
    hs_server = HostServer(hs_config)
    hs_server.HSCreate()
    hs_server.HSLoader()
    # hs_server.VMCreate(vm_config)
    hs_server.VMPowers(vm_config.vm_uuid, VMPowers.S_START)
