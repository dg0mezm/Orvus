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


    def _print_msg(self, msg, msg_type, debug):
        if msg_type == "normal":
            print(f"[+] [Orvus] {msg}")
        elif msg_type == "wrong":
            print(f"[-] [Orvus] {msg}")
        elif msg_type == "warning":
            print(f"[!] [Orvus] {msg}")
        else:
            print(f"[x] [Orvus] The Great Clock is experiencing unhandled problems!\nError: {msg}")