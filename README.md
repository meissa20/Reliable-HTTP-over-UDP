# 📡 Reliable HTTP over UDP

## Overview

This project simulates TCP-like reliability over UDP and builds a basic HTTP/1.0 client-server model that supports `GET` and `POST` requests. It is implemented using Python sockets, adding mechanisms such as:

- Stop-and-Wait ARQ
- Checksum-based error detection
- Packet loss and corruption simulation
- TCP-style handshake (SYN, SYNACK, ACK)
- Graceful teardown (FIN, ACK)
- Simple HTTP/1.0 protocol support

---

## 📁 File Structure

- 'reliableUDP.py       # Main class with reliable UDP functionality'
- 'http_client.py       # Sends HTTP GET/POST requests'
- 'http_server.py       # Handles incoming HTTP requests'
- 'test.txt             # Sample file used for GET requests'
- 'algo 1.png           # State machine for the algorithm used in reliableUDP.py'
- 'algo 2.png           # State machine for the algorithm used in reliableUDP.py'
- 'README.md            # This file'


---

## 🧠 How It Works

### Packet Format

Each packet follows this structure:

<FLAG>,<SEQ>,<DATA>,<CHECKSUM>


- `FLAG`: SYN, SYNACK, ACK, FIN, or DATA
- `SEQ`: Sequence number (0 or 1 for Stop-and-Wait)
- `DATA`: Payload (HTTP request or response)
- `CHECKSUM`: MD5 hash of the header + data

---

## ✅ Features

- Reliable transmission using Stop-and-Wait
- MD5 checksum for integrity verification
- Retransmission on timeout
- Duplicate detection and ACK resending
- TCP-style connection setup and teardown
- HTTP/1.0 GET: Returns the content of a file
- HTTP/1.0 POST: Saves the body to `post_output.txt`

---

## 🧪 How to Test

1. Create a file named `test.txt` with some content (e.g., "Luka Modric is the best midfielder in the history")
2. Run the server:
   ```bash
   python http_server.py
   python http_client.py

## 🛠 Configuration
- self.packet_loss_prob = 0.1         # 10% chance to drop packet
- self.packet_corrupt_prob = 0.1      # 10% chance to corrupt packet

## 📌 Dependencies

- Python 3.x
- No external libraries needed (uses socket, hashlib, random)

## 📎Notes
- Only one client is supported at a time
- HTTP version used is 1.0 (connection closes after each request)


