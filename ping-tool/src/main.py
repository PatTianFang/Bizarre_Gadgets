import tkinter as tk
from tkinter import ttk
import threading
from concurrent.futures import ThreadPoolExecutor
import socket
import subprocess
from utils.network import ping_ip

class PingToolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ping Tool")
        self.geometry("600x400")

        # Add dropdown menu for selecting IP range
        self.net_label = ttk.Label(self, text="Select IP range:")
        self.net_label.pack(pady=10)

        self.ip_range_options = ["192.168.1.1-192.168.1.254", "10.0.0.1-10.0.0.254", "172.16.0.1-172.16.0.254"]
        self.ip_range_selector = ttk.Combobox(self, values=self.ip_range_options, state="readonly")
        self.ip_range_selector.pack(pady=10)
        self.ip_range_selector.bind("<<ComboboxSelected>>", self.update_ip_range)

        # Display the currently selected range
        self.current_range_label = ttk.Label(self, text="Current Range: None")
        self.current_range_label.pack(pady=10)

        # Manual input for IP range
        self.label = ttk.Label(self, text="Enter IP range (e.g., 192.168.1.1-192.168.1.254):")
        self.label.pack(pady=10)

        self.ip_range_input = ttk.Entry(self, width=40)
        self.ip_range_input.pack(pady=10)

        self.ping_button = ttk.Button(self, text="Ping", command=self.start_ping)
        self.ping_button.pack(pady=10)

        # Add a Text widget to display ping process
        self.log_text = tk.Text(self, height=15, width=70, state="normal")
        self.log_text.pack(pady=10)

        self.result_label = ttk.Label(self, text="")
        self.result_label.pack(pady=10)

    def update_ip_range(self, event):
        """Update the currently selected IP range"""
        selected_range = self.ip_range_selector.get()
        self.current_range_label.config(text=f"Current Range: {selected_range}")
        self.ip_range_input.delete(0, tk.END)
        self.ip_range_input.insert(0, selected_range)

    def start_ping(self):
        ip_range = self.ip_range_input.get()
        self.result_label.config(text="Pinging...")
        self.log_text.delete(1.0, tk.END)  # Clear the log text
        threading.Thread(target=self.ping_ips, args=(ip_range,)).start()

    def ping_ips(self, ip_range):
        try:
            start_ip, end_ip = ip_range.split('-')
            start = list(map(int, start_ip.split('.')))
            end = list(map(int, end_ip.split('.')))
            reachable_ips = []

            # Generate all IPs in the range
            ip_list = [
                f"{start[0]}.{start[1]}.{i}.{j}"
                for i in range(start[2], end[2] + 1)
                for j in range(start[3], end[3] + 1)
            ]

            # Use ThreadPoolExecutor for parallel pinging
            with ThreadPoolExecutor(max_workers=20) as executor:  # Increase max_workers for more threads
                results = executor.map(self.ping_and_collect_info, ip_list)

            # Collect reachable IPs
            for result in results:
                if result:
                    reachable_ips.append(result)

            # Update the result label
            if reachable_ips:
                self.result_label.config(text="Reachable IPs: " + ", ".join(reachable_ips))
            else:
                self.result_label.config(text="No reachable IPs found.")
        except Exception as e:
            self.result_label.config(text=f"Error: {e}")

    def ping_and_collect_info(self, ip):
        """Ping an IP and collect its information"""
        self.log_message(f"Pinging {ip}...")
        if ping_ip(ip):  # Use the optimized ping function
            hostname = self.get_hostname(ip)
            mac_address = self.get_mac_address(ip)
            self.log_message(f"{ip} is reachable. Hostname: {hostname}, MAC: {mac_address}")
            return ip
        else:
            self.log_message(f"{ip} is not reachable.")
            return None

    def get_hostname(self, ip):
        """Get the hostname of a device by its IP"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except socket.herror:
            return "Unknown"

    def get_mac_address(self, ip):
        """Get the MAC address of a device by its IP"""
        try:
            result = subprocess.run(["arp", "-a", ip], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            for line in lines:
                if ip in line:
                    return line.split()[1]  # Extract MAC address
            return "Unknown"
        except Exception:
            return "Unknown"

    def log_message(self, message):
        """Log a message to the Text widget"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Scroll to the end

if __name__ == "__main__":
    app = PingToolApp()
    app.mainloop()