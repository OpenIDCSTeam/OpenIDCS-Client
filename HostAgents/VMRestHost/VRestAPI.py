import requests
from requests.auth import HTTPBasicAuth

from HostObject.VMConfig import VMConfig
from HostObject.ZMConfig import NCConfig
from HostObject.ZMessage import ZMessage
from HostObject.VMPowers import VMPowers


class VRestAPI:
    def __init__(self,
                 host_addr="localhost:8697",
                 host_user="root",
                 host_pass="password",
                 ver_agent=21):
        self.host_addr = host_addr
        self.host_user = host_user
        self.host_pass = host_pass
        self.ver_agent = ver_agent

    @staticmethod
    # 创建vmx文本 =========================================================
    def create_txt(in_config: dict, prefix: str = ""):
        result = ""
        for key, value in in_config.items():
            if isinstance(value, dict):  # 如果值是字典，递归处理 =========
                new_prefix = f"{prefix}{key}." if prefix else f"{key}."
                result += VRestAPI.create_txt(value, new_prefix)
            else:  # 如果值不是字典，直接生成配置行 =======================
                full_key = f"{prefix}{key}" if prefix else key
                if type(value) == str:
                    result += f"{full_key} = \"{value}\"\n"
                else:
                    result += f"{full_key} = {value}\n"
        return result

    # VMRestAPI ===========================================================
    def vmrest_api(self, url: str, data: dict = None, method: str = "GET") -> ZMessage:
        """
        发送VMRest API请求
        :param url: API端点路径 (如 /vms, /vms/{id}/power)
        :param data: 请求体数据 (用于POST/PUT请求)
        :param method: HTTP方法 (GET, POST, PUT, DELETE)
        :return: ZMessage对象
        """
        full_url = f"http://{self.host_addr}/api{url}"
        auth = HTTPBasicAuth(self.host_user, self.host_pass)
        headers = {"Content-Type": "application/vnd.vmware.vmw.rest-v1+json"}
        try:
            
            if method.upper() == "GET":
                response = requests.get(full_url, auth=auth, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(full_url, auth=auth, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(full_url, auth=auth, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(full_url, auth=auth, headers=headers)
            else:
                return ZMessage(
                    success=False,
                    actions="vmrest_api",
                    message=f"不支持的HTTP方法: {method}"
                )
            response.raise_for_status()
            return ZMessage(
                success=True,
                actions="vmrest_api",
                message="请求成功",
                results=response.json() if response.text else {}
            )
        except requests.exceptions.RequestException as e:
            return ZMessage(
                success=False,
                actions="vmrest_api",
                message=str(e),
                execute=e
            )

    # VMRest电源操作API（请求体为纯字符串） ================================
    def vmrest_api_power(self, url: str, power_state: str) -> ZMessage:
        """
        发送VMRest电源操作请求（PUT请求体为纯字符串）
        :param url: API端点路径
        :param power_state: 电源状态字符串 (on, off, shutdown, suspend, pause, unpause)
        :return: ZMessage对象
        """
        full_url = f"http://{self.host_addr}/api{url}"
        auth = HTTPBasicAuth(self.host_user, self.host_pass)
        headers = {"Content-Type": "application/vnd.vmware.vmw.rest-v1+json"}
        try:
            response = requests.put(full_url, auth=auth, headers=headers, data=power_state)
            response.raise_for_status()
            return ZMessage(
                success=True,
                actions="vmrest_api_power",
                message="电源操作成功",
                results=response.json() if response.text else {}
            )
        except requests.exceptions.RequestException as e:
            return ZMessage(
                success=False,
                actions="vmrest_api_power",
                message=str(e),
                execute=e
            )

    # 获取所有虚拟机列表 ==================================================
    def get_all_vm(self) -> ZMessage:
        """获取所有已注册的虚拟机列表"""
        return self.vmrest_api("/vms")
    
    # 选择虚拟机ID ========================================================
    def select_vid(self, vm_name: str) -> str:
        """根据虚拟机名称获取虚拟机ID
        :param vm_name: 虚拟机名称
        :return: 虚拟机ID，未找到返回空字符串
        """
        result = self.get_all_vm()
        if not result.success:
            return ""
        vms = result.results if isinstance(result.results, list) else []
        for vm in vms:
            # VMRest API返回的虚拟机信息包含id和path字段
            # 从path中提取虚拟机名称进行匹配
            vm_path = vm.get("path", "")
            vm_id = vm.get("id", "")
            # 方式1：直接匹配路径中的虚拟机名称
            if vm_name in vm_path:
                return vm_id
            # 方式2：提取.vmx文件名进行匹配
            import os
            vmx_name = os.path.splitext(os.path.basename(vm_path))[0]
            if vmx_name == vm_name:
                return vm_id
        return ""

    # 获取虚拟机电源状态 ==================================================
    def get_powers(self, vm_name: str) -> ZMessage:
        """获取指定虚拟机的电源状态
        :param vm_name: 虚拟机名称
        """
        vm_id = self.select_vid(vm_name)
        if not vm_id:
            return ZMessage(
                success=False,
                actions="get_powers",
                message=f"未找到虚拟机: {vm_name}"
            )
        return self.vmrest_api(f"/vms/{vm_id}/power")

    # 设置虚拟机电源状态 ==================================================
    # :param vm_name: 虚拟机名称
    # :param power_state: VMPowers枚举类型
    # :param vm_password: 加密虚拟机的密码（可选）
    # :return: ZMessage对象
    # =====================================================================
    def set_powers(self, vm_name: str, power_state: VMPowers, vm_password: str = None) -> ZMessage:
        # 电源状态映射
        power_map = {
            VMPowers.S_START: "on",
            VMPowers.S_CLOSE: "shutdown",
            VMPowers.S_RESET: "reset",
            VMPowers.H_CLOSE: "off",
            VMPowers.H_RESET: "reset",
            VMPowers.A_PAUSE: "pause",
            VMPowers.A_WAKED: "unpause",
        }
        state_str = power_map.get(power_state, "on")
        vm_id = self.select_vid(vm_name)
        if not vm_id:
            return ZMessage(
                success=False,
                actions="set_powers",
                message=f"未找到虚拟机: {vm_name}"
            )
        # 构建URL，如果有密码则添加查询参数
        url = f"/vms/{vm_id}/power"
        if vm_password:
            url += f"?vmPassword={vm_password}"
        # VMRest API要求PUT请求体为纯字符串
        return self.vmrest_api_power(url, state_str)

    # 注册虚拟机 ==========================================================
    def loader_vmx(self, vmx_path: str, vm_name: str = None) -> ZMessage:
        """注册虚拟机到VMware Workstation
        :param vmx_path: .vmx文件的完整路径
        :param vm_name: 虚拟机名称（可选，默认使用vmx文件名）
        """
        import os
        if vm_name is None:
            # 从路径中提取虚拟机名称（不含扩展名）
            vm_name = os.path.splitext(os.path.basename(vmx_path))[0]
        return self.vmrest_api(
            "/vms/registration",
            {"name": vm_name, "path": vmx_path},
            "POST")

    # 删除虚拟机 ==========================================================
    def delete_vmx(self, vm_name: str) -> ZMessage:
        """从VMware Workstation中删除虚拟机
        :param vm_name: 虚拟机名称
        """
        vm_id = self.select_vid(vm_name)
        if not vm_id:
            return ZMessage(
                success=False,
                actions="delete_vmx",
                message=f"未找到虚拟机: {vm_name}"
            )
        return self.vmrest_api(f"/vms/{vm_id}", method="DELETE")

    # 获取虚拟机配置 ======================================================
    def get_config(self, vm_name: str) -> ZMessage:
        """获取虚拟机配置信息
        :param vm_name: 虚拟机名称
        """
        vm_id = self.select_vid(vm_name)
        if not vm_id:
            return ZMessage(
                success=False,
                actions="get_config",
                message=f"未找到虚拟机: {vm_name}"
            )
        return self.vmrest_api(f"/vms/{vm_id}")

    # 更新虚拟机配置 ======================================================
    def set_config(self, vm_name: str, config: dict) -> ZMessage:
        """更新虚拟机配置
        :param vm_name: 虚拟机名称
        :param config: 配置字典
        """
        vm_id = self.select_vid(vm_name)
        if not vm_id:
            return ZMessage(
                success=False,
                actions="set_config",
                message=f"未找到虚拟机: {vm_name}"
            )
        return self.vmrest_api(f"/vms/{vm_id}", config, "PUT")

    # 获取网络列表 ========================================================
    def get_vm_net(self) -> ZMessage:
        """获取所有虚拟网络"""
        return self.vmrest_api("/vmnet")

    # 创建虚拟机 ==========================================================
    def create_vmx(self, vm_conf: VMConfig = None) -> str:
        vmx_config = {
            # 编码配置 ============================================
            ".encoding": "GBK",
            "config.version": "8",
            "virtualHW.version": str(self.ver_agent),
            # 基本配置 ============================================
            "displayName": vm_conf.vm_uuid,
            "firmware": "efi",
            "guestOS": "windows9-64",
            # 硬件配置 ============================================
            "numvcpus": str(vm_conf.cpu_num),
            "cpuid.coresPerSocket": str(vm_conf.cpu_num),
            "memsize": str(vm_conf.mem_num),
            "mem.hotadd": "TRUE",
            "mks.enable3d": "TRUE",
            "svga.graphicsMemoryKB": str(vm_conf.gpu_mem * 1024),
            # 设备配置 ============================================
            "vmci0.present": "TRUE",
            "hpet0.present": "TRUE",
            "usb.present": "TRUE",
            "ehci.present": "TRUE",
            "usb_xhci.present": "TRUE",
            "tools.syncTime": "TRUE",
            "nvram": vm_conf.vm_uuid + ".nvram",
            "virtualHW.productCompatibility": "hosted",
            "extendedConfigFile": vm_conf.vm_uuid + ".vmxf",
            # PCI桥接配置 =========================================
            "pciBridge0": {
                "present": "TRUE"
            },
            "pciBridge4": {
                "present": "TRUE",
                "virtualDev": "pcieRootPort",
                "functions": "8"
            },
            # 系统盘配置 ==========================================
            "nvme0.present": "TRUE",
            "nvme0:0": {
                "fileName": vm_conf.vm_uuid + ".vmdk",
                "present": "TRUE"
            },
            # 远程显示配置 ========================================
            "RemoteDisplay": {
                "vnc": {
                    "enabled": "TRUE",
                    "port": "5901"
                }
            }
        }
        nic_uuid = 0  # 网卡配置 ==========================================
        for nic_name, nic_data in vm_conf.nic_all.items():
            use_auto = nic_data.mac_addr is None or nic_data.mac_addr == ""
            vmx_config[f"ethernet{nic_uuid}"] = {
                "connectionType": "nat" if nic_data.nic_type == "nat" else "",
                "addressType": "generated" if use_auto else "static",
                "address": nic_data.mac_addr if use_auto else "",
                "virtualDev": "e1000e",
                "present": "TRUE",
                "txbw.limit": str(vm_conf.speed_u * 1024),
                "rxbw.limit": str(vm_conf.speed_d * 1024),
            }
            nic_uuid += 1
        hdd_uuid = 1  # 数据磁盘 ==========================================
        for hdd_name, hdd_data in vm_conf.hdd_all.items():
            # todo: 创建VMDK文件
            vmx_config[f"nvme0:{hdd_uuid}"] = {
                "fileName": vm_conf.vm_uuid + f"-{hdd_uuid}.vmdk",
                "present": "TRUE"
            }
            hdd_uuid += 1
        return VRestAPI.create_txt(vmx_config)


if __name__ == "__main__":
    vm_client = VRestAPI()
    vm_config = VMConfig(
        vm_uuid="Tests-All",
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
    vm_string = vm_client.create_vmx(vm_config)
    print(vm_string)
    with open(vm_config.vm_uuid + ".vmx", "w", encoding="utf-8") as save_file:
        save_file.write(vm_string)
