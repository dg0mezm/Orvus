import json
from src.Zoni import Zoni

class Orvus():
    def __init__(self, args):
        self.args = args
        self.ping_conectivity = False
        self.tcp_ports = []
        self.udp_ports = []

        self.scan()


    def scan(self):
        self._initial_scan()


    def _initial_scan(self):
        if self.args.ignore_ping or self._ping():
            if self.args.ignore_ping:
                self._print_msg(f"Ping was ignored.", "warning", self.args.debug)
            else:
                self._print_msg(f"{self.args.ip} is active.", "normal", self.args.debug)

            self._scan_ports()
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
        task_tcp_ports = json.dumps({
            "task": "scan_tcp_ports",
            "data": {
                "target": self.args.ip
            }
        })
        zoni_tcp_ports = Zoni(task_tcp_ports)


        task_udp_ports = json.dumps({
            "task": "scan_udp_ports",
            "data": {
                "target": self.args.ip
            }
        })
        zoni_udp_ports = Zoni(task_udp_ports)

        zoni_tcp_ports.start()
        zoni_udp_ports.start()
        zoni_tcp_ports.join()
        zoni_udp_ports.join()


    def _print_msg(self, msg, msg_type, debug):
        if msg_type == "normal":
            print(f"[+] [Orvus] {msg}")
        elif msg_type == "wrong":
            print(f"[-] [Orvus] {msg}")
        elif msg_type == "warning":
            print(f"[!] [Orvus] {msg}")
        else:
            print(f"[x] [Orvus] The Great Clock is experiencing unhandled problems!\nError: {msg}")