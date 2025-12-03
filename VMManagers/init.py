#!/usr/bin/env python3
import netifaces as ni
import yaml
from typing import Dict, List, Optional


class CloudInitNetworkConfig:
    def __init__(self, gateway: Optional[str] = None, dns: Optional[List[str]] = None):
        self.interfaces = self._get_interfaces()
        self.gateway = gateway
        self.dns = dns or ["8.8.8.8", "114.114.114.114"]

    def _get_interfaces(self) -> Dict[str, str]:
        interfaces = {}
        for iface in ni.interfaces():
            if iface == 'lo':
                continue
            try:
                mac = ni.ifaddresses(iface)[ni.AF_LINK][0]['addr']
                if mac and mac != '00:00:00:00:00:00':
                    interfaces[iface] = mac.lower()
            except (KeyError, IndexError):
                continue
        return interfaces

    def _mac_to_ip(self, mac: str) -> str:
        return ".".join(str(int(part, 16)) for part in mac.split(":")[-4:])

    def _get_gateway(self, ip: str) -> str:
        return self.gateway or ".".join(ip.split('.')[:-1] + ['1'])

    def generate(self) -> Dict:
        config = {"version": 2, "ethernets": {}}
        for iface, mac in self.interfaces.items():
            ip = self._mac_to_ip(mac)
            config["ethernets"][iface] = {
                "match": {"macaddress": mac},
                "addresses": [f"{ip}/24"],
                "routes": [{"to": "default", "via": self._get_gateway(ip)}],
                "nameservers": {"addresses": self.dns}
            }
        return config

    def save(self, filename: str = "network-config.yaml"):
        with open(filename, 'w') as f:
            yaml.dump(self.generate(), f, default_flow_style=False, allow_unicode=True)