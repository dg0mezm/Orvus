import threading
import subprocess
import json
import re


class Zoni(threading.Thread):
    def __init__(self, task_json):
        super().__init__()
        parsed = json.loads(task_json)
        self.task_name = parsed.get("task")
        self.task_data = parsed.get("data", {})
        self.task_result = None
        self.task_map = {
            "ping": self._run_ping,
            "scan_tcp_ports": self._run_scan_tcp_ports,
            "scan_udp_ports": self._run_scan_udp_ports,
        }


    def run(self):
        task_func = self.task_map.get(self.task_name)
        if task_func:
            task_func()
        else:
            self._print_msg(f"'{self.task_name}' is not implemented in the Great Clock.", "wrong")


    def _run_ping(self):
        target = self.task_data.get("target")
        self._print_msg(f"Checking conectivity to {target}...", "normal")
        result = subprocess.run(["ping", "-c", "1", "-W", "1", target], stdout=subprocess.DEVNULL)
        self.task_result = result.returncode == 0


    def _run_scan_tcp_ports(self):
        result = {}
        result['port_scan'] = self._discovery_tcp_ports()
        self._print_msg(f"The TCP Port Scan has finished.", "normal")
        if len(result['port_scan']['tcp_ports']) > 0:
            result['service_scan'] = self._enumerate_tcp_services(result['port_scan']['tcp_ports'])
            self._print_msg(f"The TCP Service Scan has finished.", "normal")
        else:
            result['service_scan'] = {}
        self.task_result = result


    def _discovery_tcp_ports(self):
        result = {}
        target = self.task_data.get("target")
        self._print_msg(f"Scanning TCP ports from {target}", "normal")
        result_command = subprocess.run(["nmap", "-sS", "-p-", "-T5", target, "--open", "-Pn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        result['output_scan'] = result_command.stdout
        result['tcp_ports'] = re.findall(r'^(\d+)/tcp\s+open', result_command.stdout, re.MULTILINE)
        return result

    
    def _enumerate_tcp_services(self, tcp_ports):
        result = {}
        target = self.task_data.get("target")
        self._print_msg(f"Scanning TCP services from {target}", "normal")
        result_command = subprocess.run(["nmap", "-sCV", f"-p{",".join(tcp_ports)}", "-A", target, "-Pn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        result['output_scan'] = result_command.stdout
        return result


    def _run_scan_udp_ports(self):
        result = {}
        result['port_scan'] = self._discovery_udp_ports()
        self._print_msg(f"The UDP Port Scan has finished.", "normal")
        if len(result['port_scan']['udp_ports']) > 0:
            result['service_scan'] = self._enumerate_udp_services(result['port_scan']['udp_ports'])
            self._print_msg(f"The UDP Service Scan has finished.", "normal")
        else:
            result['service_scan'] = {}
        self.task_result = result


    def _discovery_udp_ports(self):
        result = {}
        target = self.task_data.get("target")
        self._print_msg(f"Scanning UDP ports from {target}", "normal")
        result_command = subprocess.run(["nmap", "-sU", "-T5", target, "--open", "-Pn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        result['output_scan'] = result_command.stdout
        result['udp_ports'] = re.findall(r'^(\d+)/udp\s+open', result_command.stdout, re.MULTILINE)
        return result

    
    def _enumerate_udp_services(self, udp_ports):
        result = {}
        target = self.task_data.get("target")
        self._print_msg(f"Scanning UDP services from {target}", "normal")
        result_command = subprocess.run(["nmap", "-sCV", "-sU", f"-p{",".join(udp_ports)}", "-A", target, "-Pn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        result['output_scan'] = result_command.stdout
        return result


    def _print_msg(self, msg, msg_type):
        if msg_type == "normal":
            print(f"[+] [Zoni] {msg}")
        elif msg_type == "wrong":
            print(f"[-] [Zoni] {msg}")
        elif msg_type == "warning":
            print(f"[!] [Zoni] {msg}")
        else:
            print(f"[x] [Zoni] The Great Clock is experiencing unhandled problems!\nError: {msg}")


    def get_task_result(self):
        return self.task_result