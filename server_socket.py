import socket

def start_my_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 10000))
        server.listen(4)

        while True:
            print('Working ...')
            client_socket, _ = server.accept()
            data = client_socket.recv(1024).decode('utf-8')
            content = parse_get_request(data)
            client_socket.send(content)
            client_socket.shutdown(socket.SHUT_WR)
    except KeyboardInterrupt:
        server.close()
        print('shutdown')

def parse_get_request(request_data):
    HDRS = 'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n'
    lines = request_data.split('\n')
    status_raw, lines = lines[0], lines[1:]
    method, path_raw, _ = status_raw.split(' ')

    path = checking_path(path_raw)
    if path == None:
        return (HDRS + 'Sorry! No page ...').encode('utf-8')
    else:
        params = parse_params(path_raw)
        headers = parse_headers(lines)
        response = f'Method: {method} \r\nPath: {path} \r\nParams: {params} \r\nHeaders: {headers}\r\n'
        print(response)
        return HDRS.encode('utf-8') + response.encode('utf-8')
    
def checking_path(path):
    list_paths = ['vk.com', 'facebook.com', 'onliner.by', 'realt.by']
    tested_path, _, _ = path.partition('?')
    tested_path = tested_path.replace('/', '')
    if tested_path in list_paths:
        return tested_path
    
def parse_params(path):
    _, _, tested_params = path.partition('?')
    if tested_params == '':
        return 
    else:
        return tested_params
    
def parse_headers(lines):
    list_headers = []
    for line in lines:
        header, _, _ = line.partition(':')
        header = header.strip()
        header = header.strip('\r')
        if header == '':
            break
        else:
            list_headers.append(header)
    return list_headers

if __name__ == '__main__':
    start_my_server()
