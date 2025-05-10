from thinker import App, Button, TextBox, Label

class PingToolApp(App):
    def __init__(self):
        super().__init__()
        self.title = "Ping Tool"
        self.ip_range_input = TextBox(self, placeholder="Enter IP range (e.g., 192.168.1.1-192.168.1.254)")
        self.ping_button = Button(self, text="Ping", command=self.ping_ips)
        self.result_label = Label(self)

        self.layout()

    def layout(self):
        self.ip_range_input.pack()
        self.ping_button.pack()
        self.result_label.pack()

    def ping_ips(self):
        ip_range = self.ip_range_input.get()
        start_ip, end_ip = self.parse_ip_range(ip_range)
        reachable_ips = self.check_reachable_ips(start_ip, end_ip)
        self.result_label.text = "Reachable IPs: " + ", ".join(reachable_ips)

    def parse_ip_range(self, ip_range):
        start_ip, end_ip = ip_range.split('-')
        return start_ip.strip(), end_ip.strip()

    def check_reachable_ips(self, start_ip, end_ip):
        from utils.network import ping_ip_range
        return ping_ip_range(start_ip, end_ip)

if __name__ == "__main__":
    app = PingToolApp()
    app.run()