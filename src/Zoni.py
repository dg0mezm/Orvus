import threading
import subprocess
import json

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
        target = self.task_data.get("target")
        self._print_msg(f"Scanning TCP ports from {target}", "normal")
        result = subprocess.run(["nmap", "-sS", "-p-", "-T5", target, "--open", "-Pn"])


    def _run_scan_udp_ports(self):
        target = self.task_data.get("target")
        self._print_msg(f"Scanning TCP ports from {target}", "normal")
        result = subprocess.run(["nmap", "-sU", "-T5", target, "--open", "-Pn"])


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