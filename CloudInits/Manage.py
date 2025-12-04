import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class CloudinitConfig:
    """
    Cloudinit/Cloudbase-Init 配置生成器
    支持Linux(cloud-init)和Windows(Cloudbase-Init)虚拟机
    """

    def __init__(self, os_type: str, vm_list: List[Dict[str, str]],
                 report_host: str, hostname: str = "vm-template",
                 iso_output_dir: str = "./"):
        """
        初始化配置生成器

        :param os_type: 系统类型 - "linux" 或 "windows"
        :param vm_list: 虚拟机网络配置列表，格式: [{"mac": "00:50:56:XX:XX:XX", "ip": "192.168.1.100"}]
        :param report_host: 状态上报主机地址，如 "http://192.168.1.10:8080/api/vms"
        :param hostname: 虚拟机主机名
        :param iso_output_dir: ISO输出目录
        """
        self.os_type = os_type.lower()
        if self.os_type not in ["linux", "windows"]:
            raise ValueError("os_type must be 'linux' or 'windows'")

        self.vm_list = vm_list
        self.report_host = report_host
        self.hostname = hostname
        self.iso_output_dir = Path(iso_output_dir)
        self.iso_output_dir.mkdir(parents=True, exist_ok=True)

        # 验证VM列表格式
        self._validate_vm_list()

    def _validate_vm_list(self):
        """验证虚拟机列表格式"""
        for vm in self.vm_list:
            if "mac" not in vm or "ip" not in vm:
                raise ValueError("每个VM必须包含'mac'和'ip'字段")
            # 简单验证MAC格式
            if not self._is_valid_mac(vm["mac"]):
                raise ValueError(f"无效的MAC地址: {vm['mac']}")
            # 简单验证IP格式
            if not self._is_valid_ip(vm["ip"]):
                raise ValueError(f"无效的IP地址: {vm['ip']}")

    @staticmethod
    def _is_valid_mac(mac: str) -> bool:
        """验证MAC地址格式"""
        parts = mac.replace("-", ":").split(":")
        if len(parts) != 6:
            return False
        return all(len(p) == 2 and set(p) <= set("0123456789abcdefABCDEF") for p in parts)

    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        """验证IP地址格式"""
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except ValueError:
            return False

    def _generate_meta_data(self) -> Dict:
        """生成meta_data.json"""
        return {
            "uuid": f"{self.hostname}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "hostname": self.hostname,
            "name": self.hostname,
            "public_keys": {},  # 可根据需要添加SSH密钥
            "availability_zone": "az1",
            "launch_index": 0,
            "meta": {
                "os_type": self.os_type,
                "report_host": self.report_host
            }
        }

    def _generate_network_data(self) -> Dict:
        """生成network_data.json - OpenStack格式"""
        networks = []
        links = []

        for idx, vm in enumerate(self.vm_list):
            link_id = f"eth{idx}" if self.os_type == "linux" else f"ethernet{idx}"
            network_id = f"network{idx}"

            # 生成link配置
            links.append({
                "id": link_id,
                "name": link_id,
                "type": "phy",
                "ethernet_mac_address": vm["mac"].upper(),
                "mtu": 1500
            })

            # 生成网络配置
            networks.append({
                "id": network_id,
                "type": "ipv4",
                "link": link_id,
                "ip_address": vm["ip"],
                "netmask": "255.255.255.0",
                "routes": [
                    {
                        "network": "0.0.0.0",
                        "netmask": "0.0.0.0",
                        "gateway": self._guess_gateway(vm["ip"])
                    }
                ],
                "services": [
                    {"type": "dns", "address": "8.8.8.8"},
                    {"type": "dns", "address": "114.114.114.114"}
                ]
            })

        return {
            "links": links,
            "networks": networks
        }

    def _guess_gateway(self, ip: str) -> str:
        """根据IP猜测网关（假设为.x.1）"""
        parts = ip.split(".")
        parts[3] = "1"
        return ".".join(parts)

    def _generate_linux_user_data(self) -> str:
        """生成Linux user_data (cloud-init)"""
        # 上报脚本
        report_script = f"""
#!/bin/bash
sleep 30  # 等待网络完全就绪
HOSTNAME=$(hostname)
MACS="{','.join([vm['mac'] for vm in self.vm_list])}"
IPS="{','.join([vm['ip'] for vm in self.vm_list])}"

curl -X POST {self.report_host} \
  -H "Content-Type: application/json" \
  -d "{{\\"hostname\\": \\"$HOSTNAME\\", \\"mac\\": \\"$MACS\\", \\"ip\\": \\"$IPS\\", \\"status\\": \\"ready\\", \\"os\\": \\"linux\\", \\"timestamp\\": \\"$(date -Iseconds)\\"}}" \
  --retry 3 --retry-delay 5
"""

        return f"""#cloud-config

# Hostname
hostname: {self.hostname}
fqdn: {self.hostname}.local

# Update packages
package_update: true
package_upgrade: true

# Create report script
write_files:
  - path: /usr/local/bin/report-status.sh
    content: |
      {report_script.strip()}
    permissions: '0755'

# Run report script after boot
runcmd:
  - systemctl start systemd-networkd || systemctl restart networking
  - /usr/local/bin/report-status.sh

# Ensure report runs even if network is slow
bootcmd:
  - 'echo "Waiting for network..."'
"""

    def _generate_windows_user_data(self) -> str:
        """生成Windows user_data (Cloudbase-Init)"""
        # 上报脚本 (PowerShell)
        mac_list = ",".join([vm['mac'] for vm in self.vm_list])
        ip_list = ",".join([vm['ip'] for vm in self.vm_list])

        report_script = f"""
$retryCount = 3
$retryDelay = 5
$count = 0
$success = $false

while ($count -lt $retryCount -and -not $success) {{
    try {{
        $body = @{{
            hostname = $env:COMPUTERNAME
            mac = "{mac_list}"
            ip = "{ip_list}"
            status = "ready"
            os = "windows"
            timestamp = (Get-Date -Format o)
        }} | ConvertTo-Json

        Invoke-WebRequest -Uri "{self.report_host}" `
            -Method POST `
            -Body $body `
            -ContentType "application/json" `
            -TimeoutSec 30

        Write-Output "Status reported successfully"
        $success = $true
    }} catch {{
        Write-Output "Failed to report status: $_.Exception.Message"
        $count++
        Start-Sleep -Seconds $retryDelay
    }}
}}

if (-not $success) {{
    Write-Output "Failed to report status after $retryCount attempts"
    # 写入本地日志
    $body | Out-File -FilePath "C:\\cloudinit-report-failed.log" -Append
}}
"""

        return f"""#cloud-config

# Set hostname
set_hostname: {self.hostname}

# Enable RDP
set_rdp_status: enabled

# Create PowerShell report script
write_files:
  - path: C:\\CloudInit\\report-status.ps1
    content: |
      {report_script.strip()}
    permissions: '0644'

# Run report script
runcmd:
  - 'powershell.exe -ExecutionPolicy Bypass -File C:\\CloudInit\\report-status.ps1'

# Ensure Cloudbase-Init runs with admin privileges
# This is the default, but explicitly setting for clarity
cloudbaseinit:
  plugins:
    - cloudbaseinit.plugins.common.networkconfig.NetworkConfigPlugin
    - cloudbaseinit.plugins.common.setuserpassword.SetUserPasswordPlugin
    - cloudbaseinit.plugins.common.userdata.UserDataPlugin
"""

    def _generate_user_data(self) -> str:
        """生成user_data"""
        if self.os_type == "linux":
            return self._generate_linux_user_data()
        else:
            return self._generate_windows_user_data()

    def generate_iso(self) -> Path:
        """
        生成Config Drive ISO文件

        :return: ISO文件路径
        """
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 创建目录结构
            openstack_dir = temp_path / "openstack" / "latest"
            openstack_dir.mkdir(parents=True, exist_ok=True)

            # 生成配置文件
            meta_data = self._generate_meta_data()
            network_data = self._generate_network_data()
            user_data = self._generate_user_data()

            # 写入文件
            with open(openstack_dir / "meta_data.json", "w") as f:
                json.dump(meta_data, f, indent=2)

            with open(openstack_dir / "network_data.json", "w") as f:
                json.dump(network_data, f, indent=2)

            with open(openstack_dir / "user_data", "w") as f:
                f.write(user_data)

            # 生成ISO文件名
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            iso_filename = self.iso_output_dir / f"cloudinit-{self.hostname}-{timestamp}.iso"

            # 生成ISO
            self._create_iso(temp_path, iso_filename)

            return iso_filename

    def _create_iso(self, source_dir: Path, output_iso: Path):
        """创建ISO文件"""
        # 优先使用genisoimage，其次mkisofs，最后oscdimg
        iso_tools = [
            ("genisoimage", ["genisoimage", "-output", str(output_iso), "-V", "config-2", "-r", "-J", str(source_dir)]),
            ("mkisofs", ["mkisofs", "-o", str(output_iso), "-V", "config-2", "-r", "-J", str(source_dir)]),
        ]

        success = False

        for tool_name, cmd in iso_tools:
            try:
                # 检查工具是否存在
                subprocess.run([tool_name, "--version"],
                               capture_output=True, check=True)

                # 生成ISO
                subprocess.run(cmd, check=True, capture_output=True)
                success = True
                print(f"✅ 使用 {tool_name} 生成ISO成功: {output_iso}")
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        if not success:
            # Windows上使用oscdimg
            try:
                oscdimg_path = self._find_oscdimg()
                if oscdimg_path:
                    cmd = [
                        str(oscdimg_path),
                        "-lconfig-2",
                        "-h",
                        "-m",
                        "-o",
                        str(source_dir),
                        str(output_iso)
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    print(f"✅ 使用 oscdimg 生成ISO成功: {output_iso}")
                    success = True
            except Exception as e:
                print(f"❌ oscdimg 失败: {e}")

        if not success:
            raise RuntimeError("无法找到可用的ISO生成工具。请安装genisoimage、mkisofs或oscdimg。")

    @staticmethod
    def _find_oscdimg() -> Optional[Path]:
        """查找Windows的oscdimg工具"""
        # 常见安装路径
        possible_paths = [
            Path(
                "C:/Program Files (x86)/Windows Kits/10/Assessment and Deployment Kit/Deployment Tools/amd64/Oscdimg/oscdimg.exe"),
            Path(
                "C:/Program Files/Windows Kits/10/Assessment and Deployment Kit/Deployment Tools/amd64/Oscdimg/oscdimg.exe"),
            Path(
                "C:/Program Files (x86)/Windows Kits/8.1/Assessment and Deployment Kit/Deployment Tools/amd64/Oscdimg/oscdimg.exe"),
        ]

        for path in possible_paths:
            if path.exists():
                return path

        # 尝试从环境变量
        adk_path = os.environ.get("ADK_PATH")
        if adk_path:
            adk_bin = Path(adk_path) / "DeploymentTools" / "amd64" / "Oscdimg" / "oscdimg.exe"
            if adk_bin.exists():
                return adk_bin

        return None


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例：配置一个Windows虚拟机，双网卡
    windows_config = CloudinitConfig(
        os_type="windows",
        vm_list=[
            {"mac": "00:50:56:01:2A:3B", "ip": "192.168.1.100"},
            {"mac": "00:50:56:01:2A:3C", "ip": "10.0.0.50"}
        ],
        report_host="http://192.168.1.10:8080/api/vms/status",
        hostname="win-biz-server-01",
        iso_output_dir="./iso-output"
    )

    iso_path = windows_config.generate_iso()
    print(f"🖥️ Windows ISO生成完成: {iso_path}")

    # 示例：配置一个Linux虚拟机，单网卡
    linux_config = CloudinitConfig(
        os_type="linux",
        vm_list=[
            {"mac": "00:50:56:02:3B:4C", "ip": "192.168.1.101"}
        ],
        report_host="http://192.168.1.10:8080/api/vms/status",
        hostname="ubuntu-web-01",
        iso_output_dir="./iso-output"
    )

    iso_path = linux_config.generate_iso()
    print(f"🐧 Linux ISO生成完成: {iso_path}")