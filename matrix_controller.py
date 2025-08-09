"""
This module will contain the core logic for controlling the HDMI matrix.
"""
import socket
import time
import subprocess
import sys
import requests
class MatrixController:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1)  # Set a timeout for socket operations

    def route(self, input_port: int, output_port: int):
        """Constructs and sends a UDP packet to route an input to an output."""
        command = f"Routing Input {input_port} to Output {output_port}"
        packet_cmd = f"{input_port}V{output_port}."
        self.udp_send(packet_cmd, self.ip_address, self.port)
        return command

    def recall_preset(self, preset_num):
        """Recalls a preset from the matrix."""
        command = f"Recalling Preset {preset_num}"
        packet_cmd = f"Recall{preset_num:02d}."
        self.udp_send(packet_cmd, self.ip_address, self.port)
        return command

    def store_preset(self, preset_num):
        """Stores the current routing to a preset in the matrix."""
        command = f"Storing Preset {preset_num}"
        packet_cmd = f"Save{preset_num:02d}."
        self.udp_send(packet_cmd, self.ip_address, self.port)
        return command

    def route_all(self, input_port: int):
        """Routes the selected input to all outputs."""
        packet_cmd = f"{input_port}All"
        self.udp_send(packet_cmd, self.ip_address, self.port)
    
    def route_1_to_1(self):
        packet_cmd = "All#."
        self.udp_send(packet_cmd, self.ip_address, self.port)


    def udp_send(self, string_data: str, ip_address: str, port: int = 20107):
        """
        Sends a UDP packet with the given string data to the specified IP address and port.
        """
        print(f"Sending command: {string_data} to {ip_address}:{port}")
        bytes_data = string_data.encode('utf-16')
        bytes2 = bytearray(len(bytes_data) // 2)

        # Extract every second byte from the UTF-8 encoded data
        for b in range(len(bytes2)):
            bytes2[b] = bytes_data[b * 2]
    
        # Create a UDP socket and send the data
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        end_point = (ip_address, port)
        self.socket.sendto(bytes2, end_point)
        time.sleep(0.05) # Add 50ms delay
        self.socket.close()

    def check_connection(self):
        """Checks if the matrix is reachable via ping."""
       # check ping
        try:
            count_param = "-c" if sys.platform != "win32" else "-n"
            output = subprocess.check_output(["ping", count_param, "1", self.ip_address], stderr=subprocess.STDOUT, universal_newlines=True)
            if sys.platform == "win32":
                return "TTL=" in output
            else:
                return "1 received" in output or "1 packets received" in output
        except subprocess.CalledProcessError:
            return False
