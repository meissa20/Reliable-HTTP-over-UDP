import socket
import hashlib
import random

class ReliableUDPConnection:
    def __init__(self, is_server=False, ip='127.0.0.1', port=8000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = (ip, port)
        self.is_server = is_server
        self.last_acknowledged_seq = -1       
        if self.is_server:
            self.sock.bind(self.address)
            print(f"[SERVER] Listening on {self.address}")
        else:
            print(f"[CLIENT] Ready to send to {self.address}")
        
        self.sock.settimeout(5)
        self.c=0
        self.packet_loss_prob = 0.3         # Why Use This?
        self.packet_corrupt_prob = 0.1      # Testing network protocols: Simulates real-world unreliability.
                                            # Debugging: Ensures your code handles packet loss/corruption gracefully.
        self.sequence_number = 0
        
    def connect(self):
        syn_packet = self.make_pkt(flag='SYN',  data='', seq=self.sequence_number)
        self.sock.sendto(syn_packet, self.address)
        print(f"[CONNECT] SYN sent{syn_packet}")
        
        try:
            response, _ = self.sock.recvfrom(1024)
            flag, seq, data, checksum = self.parse_packet(response)
            if flag == 'SYNACK':
                print("[CONNECT] Received SYNACK")
                ack_packet = self.make_pkt(flag='ACK', seq=self.sequence_number, data='')
                self.sock.sendto(ack_packet, self.address)
                print("[CONNECT] Connection established")
                return True

        except socket.timeout:
            print("[TIMEOUT] No response to SYN")
            return False

    def accept(self):
        while True:
            try:
                packet, addr = self.sock.recvfrom(1024)
                flag, seq, data, checksum = self.parse_packet(packet)
                if flag == 'SYN':
                    print("[ACCEPT] SYN received from", addr)
                    synack_packet = self.make_pkt(flag='SYNACK', seq=0, data='')
                    self.sock.sendto(synack_packet, addr)
                    print("[ACCEPT] SYNACK sent")

                    ack_packet, _ = self.sock.recvfrom(1024)
                    ack_flag, _, _, _ = self.parse_packet(ack_packet)
                    if ack_flag == 'ACK':
                        print("[ACCEPT] ACK received. Connection established.\n\n")
                        self.peer_address = addr
                        return addr                   
            except socket.timeout:
                print("[TIMEOUT] Waiting for SYN")
                
    def real_sending(self, packet, address):
        if not self.simulate_packet_loss():
            if self.simulate_corruption():
                corrupted_packet = packet[:-1] + b'X'   # b'1:hello:a1bX'
                self.sock.sendto(corrupted_packet, self.address)
                print("[SEND] Corrupted packet sent")
            else:
                self.sock.sendto(packet, address)
                print("[SEND] Packet sent")
        else:
            print("[SEND] Simulated packet loss")
            
    def send(self, data, address):
        self.sequence_number = 0
        ack_received = False
        packet = self.make_pkt('DATA', data, self.sequence_number)
        while not ack_received:
            self.real_sending(packet, address)
            try:
                response, _ = self.sock.recvfrom(1024)  # 1024 bytes (max data it can read at once).
                if response.decode() == f"ACK,{self.sequence_number}":
                    print("[ACK] Received:", response.decode())
                    if  self.sequence_number == 1:
                        ack_received = True
                        self.sequence_number = 0
                    else:
                        self.sequence_number = 1
                        packet = self.make_pkt('DATA', data, self.sequence_number)
                else:
                    print("[ACK] Wrong ACK or corrupted")
            except socket.timeout:
                print("[TIMEOUT] No ACK received, resending...")
    
    def receive(self):
        
        while True:
            try:
                packet, addr = self.sock.recvfrom(1024)
                print("[RECV] Packet received:", packet)
                
                flag, seq_num, data, recv_checksum = self.parse_packet(packet)
                
                calc_checksum = self.calculate_checksum(flag.encode() + b',' + seq_num + b',' + data.encode())
                seq_num = int(seq_num)
                if calc_checksum != recv_checksum:
                    print("[ERROR] Checksum mismatch. Packet dropped.")
                    continue
                
                if seq_num == self.last_acknowledged_seq:
                    ack = f"ACK,{seq_num}".encode()
                    self.sock.sendto(ack, addr)
                    print("[DUPLICATE] Resent ACK for seq", seq_num)
                    continue
                
                if seq_num == 1:
                    print("[RECV] Valid packet with seq", seq_num, "and data:", data)
                else:
                    print("[RECV] Valid packet with seq", seq_num, "and data:", data)
                self.last_acknowledged_seq = seq_num
                
                ack = f"ACK,{seq_num}".encode()
                self.sock.sendto(ack, addr)
                print("[ACK] Sent:", ack.decode())
                if seq_num == 1:
                    return data
            
            except socket.timeout:
                print("[TIMEOUT] Waiting for packet...")
            
    def close(self):
        fin_packet = self.make_pkt(flag='FIN', data='', seq=self.sequence_number)
        self.sock.sendto(fin_packet, self.address)
        print("[CLOSE] FIN sent")

        try:
            response, _ = self.sock.recvfrom(1024)
            flag, _, _, _ = self.parse_packet(response)
            if flag == 'ACK':
                print("[CLOSE] Connection closed gracefully")
        except socket.timeout:
            print("[CLOSE] No ACK for FIN, assuming connection closed")
    
    def Accept_close(self):
        while True:
            try:
                packet, addr = self.sock.recvfrom(1024)
                flag, seq, data, checksum = self.parse_packet(packet)
                if flag == 'FIN':
                    print("[CLOSE] FIN received from client.")
                    
                    ack_packet = self.make_pkt(flag='ACK', data='', seq=seq)
                    self.sock.sendto(ack_packet, addr)
                    print("[CLOSE] ACK sent. Connection closed.")
                    return True

            except socket.timeout:
                print("[TIMEOUT] Waiting for FIN...")          
                
    def calculate_checksum(self, packet):
        return hashlib.md5(packet).hexdigest()  # Generates a 128-bit hash in binary form sth like an id for the data then convert it into a readable hexadecimal string
    
    def simulate_packet_loss(self):
        return random.random() < self.packet_loss_prob

    def simulate_corruption(self):
        return random.random() < self.packet_corrupt_prob

    def make_pkt(self, flag, data, seq):
        payload = data.encode()  # b'hello'
        header = f"{flag},{seq},".encode() # b'None:1:'
        checksum = self.calculate_checksum(header + payload).encode()  # b'a1b2'
        return header + payload + b',' + checksum # b'None:1:hello:a1b2'

    def parse_packet(self, packet):
        try:
            parts = packet.split(b',', 3)
            flag = parts[0].decode()
            seq = parts[1]
            data = parts[2].decode()
            checksum = parts[3].decode()
            return flag, seq, data, checksum
        except:
            return None, None, None, None