from reliableUDP import ReliableUDPConnection

def parse_http_request(request):
    lines = request.split('\r\n')
    if not lines:
        return None, None
    method, _, _ = lines[0].split()
    return method

def parse_http_get_request(request):
    lines = request.split('\r\n')
    if not lines:
        return None, None
    method, path, _ = lines[0].split()
    return method, path
            # GET /hello.txt HTTP/1.1\r\n
            # Host: example.com\r\n
            # User-Agent: curl/7.68.0\r\n
            # \r\n

def parse_http_post_request(request):
    headers_and_body = request.split('\r\n\r\n', 1)
    headers = headers_and_body[0]
    body = headers_and_body[1] if len(headers_and_body) > 1 else ""
    
    return body
            # GET /hello.txt HTTP/1.1\r\n
            # Host: example.com\r\n
            # User-Agent: curl/7.68.0\r\n
            # \r\n



def build_http_response(status_code, body):
    
    status_line = {
        200: "HTTP/1.0 200 OK",
        404: "HTTP/1.0 404 Not Found"
    }.get(status_code, "HTTP/1.0 500 Internal Server Error")
    
    headers = [
        f"Content-Length: {len(body)}",
        "Content-Type: text/plain",
        "",
        ""
    ]
    
    return status_line + "\r\n" + "\r\n".join(headers) + body

def main():
    
    server = ReliableUDPConnection(is_server=True, ip='127.0.0.1', port=8000)
    
    address = server.accept()

    request = server.receive()
    print("\n[SERVER] Received HTTP request:\n", request)
    
    method = parse_http_request(request)
    
    if method == 'GET':
        method, path = parse_http_get_request(request)
        print(f"[SERVER] Method: {method}, Path: {path}")
        filename = path.strip('/')
        try:
            with open(filename, 'r') as f:
                content = f.read()
                response = build_http_response(200, content)
        except FileNotFoundError:
            response = build_http_response(404, "")
    elif method == 'POST':
        try:
            body = parse_http_post_request(request)
            print(f"[SERVER] Method: {method}, body: {body}")
            with open('test.txt', 'w') as f:
                f.write(body)
            print("[SERVER] POST body saved to post_output.txt")
            response = build_http_response(200, "POST received")
        except Exception as e:
            print("[SERVER] Error handling POST:", e)
            response = build_http_response(500, "Error")

    else:
        response = build_http_response(404, "")
    server.send(response, address)
    
    server.Accept_close()

if __name__ == "__main__":
    main()