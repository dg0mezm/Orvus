import os
import sys
import json
from src.Zoni import Zoni

class Orvus():
    def __init__(self, args):
        self.args = args
        self.ping_conectivity = False
        self.tcp_scan = {}
        self.udp_scan = {}
        self.services = {}

        self._setup_work_dir()
        self.scan()


    def scan(self):
        self._initial_scan()
        self._nmap_services()


    def _initial_scan(self):
        if self.args.ignore_ping or self._ping():
            if self.args.ignore_ping:
                self._print_msg(f"Ping was ignored.", "warning", self.args.debug)
            else:
                self._print_msg(f"{self.args.ip} is active.", "normal", self.args.debug)

            self._scan_ports()
            self._save_initial_scan_into_files()
        else:
            self._print_msg(f"{self.args.ip} not responding to ping.", "wrong", self.args.debug)


    def _ping(self):
        task = json.dumps({
            "task": "ping",
            "data": {
                "target": self.args.ip
            }
        })
        zoni = Zoni(task)
        zoni.start()
        zoni.join()

        self.ping_conectivity = zoni.get_task_result()
        return self.ping_conectivity


    def _scan_ports(self):
        self._print_msg(f"Started the Port and Service Scan from {self.args.ip}", "normal", self.args.debug)
        zoni_tcp = self._scan_tcp_ports()
        zoni_udp = self._scan_udp_ports()

        zoni_tcp.join()
        zoni_udp.join()

        self.tcp_scan = zoni_tcp.task_result
        self.udp_scan = zoni_udp.task_result
        self._print_msg(f"The Port and Service Scan has finished.", "normal", self.args.debug)


    def _scan_tcp_ports(self):
        task_scan_tcp_ports = json.dumps({
            "task": "scan_tcp_ports",
            "data": {
                "target": self.args.ip
            }
        })
        zoni = Zoni(task_scan_tcp_ports)

        zoni.start()
        return zoni


    def _scan_udp_ports(self):
        task_scan_udp_ports = json.dumps({
            "task": "scan_udp_ports",
            "data": {
                "target": self.args.ip
            }
        })
        zoni = Zoni(task_scan_udp_ports)

        zoni.start()
        return zoni


    def _nmap_services(self):
        self._nmap_tcp_services()
        self._nmap_udp_services()
        self._save_nmap_scan_into_files()


    def _nmap_tcp_services(self):
        result = []
        zonis_service_scanner = []
        tcp_ports = self.tcp_scan['port_scan']['tcp_ports']
        for port in tcp_ports:
            task_nmap_tcp_service = json.dumps({
                "task": "nmap_tcp_service",
                "data": {
                    "target": self.args.ip,
                    "port": port
                }
            })
            zoni = Zoni(task_nmap_tcp_service)

            zoni.start()
            zonis_service_scanner.append(zoni)

        for zoni in zonis_service_scanner:
            zoni.join()

        for zoni in zonis_service_scanner:
            result.append(zoni.get_task_result())

        self.services['tcp'] = result


    def _nmap_udp_services(self):
        result = []
        zonis_service_scanner = []
        udp_ports = self.udp_scan['port_scan']['udp_ports']
        for port in udp_ports:
            task_nmap_udp_service = json.dumps({
                "task": "nmap_udp_service",
                "data": {
                    "target": self.args.ip,
                    "port": port
                }
            })
            zoni = Zoni(task_nmap_udp_service)

            zoni.start()
            zonis_service_scanner.append(zoni)

        for zoni in zonis_service_scanner:
            zoni.join()

        for zoni in zonis_service_scanner:
            result.append(zoni.get_task_result())

        self.services['udp'] = result
    

    def _save_initial_scan_into_files(self):
        enum_dir = os.path.join(self.args.work_dir, "enum")

        output_file = os.path.join(enum_dir, "nmap_tcp_ports.txt")
        with open(output_file, 'w') as file:
            file.write(self.tcp_scan['port_scan']['output_scan'])
        
        if 'output_scan' in self.tcp_scan['service_scan']:
            output_file = os.path.join(enum_dir, "nmap_tcp_services.txt")
            with open(output_file, 'w') as file:
                file.write(self.tcp_scan['service_scan']['output_scan'])
       

        output_file = os.path.join(enum_dir, "nmap_udp_ports.txt")
        with open(output_file, 'w') as file:
            file.write(self.udp_scan['port_scan']['output_scan'])

        if 'output_scan' in self.udp_scan['service_scan']:
            output_file = os.path.join(enum_dir, "nmap_udp_services.txt")
            with open(output_file, 'w') as file:
                file.write(self.udp_scan['service_scan']['output_scan'])


    def _save_nmap_scan_into_files(self):
        enum_dir = os.path.join(self.args.work_dir, "enum")

        for tcp_service in self.services['tcp']:
            for key in tcp_service:
                service_directory = os.path.join(enum_dir, f"{key}_tcp")
                os.makedirs(service_directory, exist_ok=True)
                output_file = os.path.join(service_directory, f"nmap_{key}.txt")
                with open(output_file, 'w') as file:
                    file.write(tcp_service[f'{key}']['nmap'])

        for udp_service in self.services['udp']:
            for key in udp_service:
                service_directory = os.path.join(enum_dir, f"{key}_udp")
                os.makedirs(service_directory, exist_ok=True)
                output_file = os.path.join(service_directory, f"nmap_{key}.txt")
                with open(output_file, 'w') as file:
                    file.write(udp_service[f'{key}']['nmap'])


    def _setup_work_dir(self):
        if not os.path.isdir(self.args.work_dir):
            os.makedirs(self.args.work_dir, exist_ok=True)
        os.makedirs(os.path.join(self.args.work_dir, "enum"), exist_ok=True)


    def _print_msg(self, msg, msg_type, debug):
        if msg_type == "normal":
            print(f"[+] [Orvus] {msg}")
        elif msg_type == "wrong":
            print(f"[-] [Orvus] {msg}")
        elif msg_type == "warning":
            print(f"[!] [Orvus] {msg}")
        else:
            print(f"[x] [Orvus] The Great Clock is experiencing unhandled problems!\nError: {msg}")