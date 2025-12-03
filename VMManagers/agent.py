import os
import platform
import netifaces as ni
import subprocess


class NetworkConfiguratorService:
    def __init__(self):
        self.interfaces = self.get_network_interfaces()
        self.netmask = "255.255.255.0"

    def get_network_interfaces(self):
        """
        获取所有网络接口及其MAC地址
        """
        interfaces = {}

        for interface in ni.interfaces():
            print(interface)
            try:
                print(ni.ifaddresses(interface))
                print(ni.ifaddresses(interface)[ni.AF_LINK])
                mac = ni.ifaddresses(interface)[ni.AF_LINK][0]['addr']
                if mac != '00:00:00:00:00:00':  # 排除无效MAC地址
                    interfaces[interface.lower()] = mac
            except KeyError:
                continue
        return interfaces

    def mac_to_ip(self, mac):
        """
        将MAC地址的后32位转换为IP地址
        """
        mac_parts = mac.split(":")
        ip_parts = mac_parts[-4:]  # 取MAC地址的后4个部分
        ip_address = ".".join(str(int(part, 16)) for part in ip_parts)  # 转换为十进制
        return ip_address

    def get_default_gateway(self):
        """
        获取当前默认网关
        """
        gateways = ni.gateways()
        default_gateway = gateways.get('default', {}).get(ni.AF_INET, (None,))[0]
        return default_gateway

    def set_ip_address(self, interface, ip_address, netmask, gateway):
        """
        设置网卡的IP地址、子网掩码和网关
        """
        os_type = platform.system()
        if os_type == "Linux":
            try:
                # 设置IP地址和子网掩码
                subprocess.run(["sudo", "ifconfig", interface, ip_address, "netmask", netmask], check=True)
                # 设置默认网关
                if gateway:
                    subprocess.run(["sudo", "route", "add", "default", "gw", gateway, interface], check=True)
                print(f"Set IP address {ip_address} with netmask {netmask} and gateway {gateway} for {interface}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to set IP address for {interface}: {e}")
        elif os_type == "Windows":
            try:
                # 设置IP地址、子网掩码和网关
                command = f"netsh interface ipv4 set address name=\"{interface}\" static {ip_address} {netmask} {gateway}"
                subprocess.run([command], check=True, shell=True)
                print(f"Set IP address {ip_address} with netmask {netmask} and gateway {gateway} for {interface}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to set IP address for {interface}: {e}")
        else:
            print("Unsupported operating system.")

    def configure_interfaces(self):
        """
        配置所有网络接口
        """
        default_gateway = self.get_default_gateway()
        print(f"Using default gateway: {default_gateway}")
        for interface, mac in self.interfaces.items():
            ip_address = self.mac_to_ip(mac)
            print(self.interfaces.items())
            # self.set_ip_address(interface, ip_address, self.netmask, default_gateway)

    def start_service(self):
        """
        启动服务
        """
        print("Starting Network Configurator Service...")
        self.configure_interfaces()
        print("Network configuration completed.")


if __name__ == "__main__":
    service = NetworkConfiguratorService()
    service.start_service()
