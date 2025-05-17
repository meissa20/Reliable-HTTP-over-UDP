from reliableUDP import ReliableUDPConnection

def build_http_get_request(path, host):
    request_lines = [
        f"GET {path} HTTP/1.0",
        f"Host: {host}",
        "",  # empty line = end of headers
        ""
    ]
    return "\r\n".join(request_lines)

def build_http_post_request(path, host, body):
    return "\r\n".join([
        f"POST {path} HTTP/1.0",
        f"Host: {host}",
        f"Content-Length: {len(body)}",
        "",
        body
    ])
    
def main():
    client = ReliableUDPConnection(is_server=False, ip='127.0.0.1', port=8000)

    if not client.connect():
        print("[CLIENT] Connection failed.")
        return
    
    method = input("Enter method (GET or POST): ").strip().upper()

    if method == "GET":
        path = "/test.txt"
        host = "localhost"
        http_request = build_http_get_request(path, host)
        print("[CLIENT] Sending GET request:\n", http_request)
    
    elif method == "POST":
        path = "/submit"
        body = "Luka Modric is the best midfielder in history"
        http_request = build_http_post_request(path, "localhost", body)
        print("[CLIENT] Sending Post request:\n", http_request)
    else:
        print("Invalid method.")
        return
    
    address = ('127.0.0.1', 8000)
    client.send(http_request, address)
    
    response = client.receive()
    print("\n[CLIENT] Received response:\n", response)
    
    client.close()

if __name__ == "__main__":
    main()