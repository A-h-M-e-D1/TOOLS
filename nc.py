import socket
import threading
import subprocess
import argparse
import sys

def run_command(command):
    command = command.rstrip()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    except Exception as e:
        output = f"Failed to execute command: {str(e)}\r\n".encode('utf-8')
    return output

def handle_client(client_socket, execute, command, upload_destination):
    if upload_destination:
        file_buffer = b""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        try:
            with open(upload_destination, 'wb') as f:
                f.write(file_buffer)
            client_socket.send(f'Successfully saved file to {upload_destination}\r\n'.encode('utf-8'))
        except Exception as e:
            client_socket.send(f'Failed to save file to {upload_destination}: {str(e)}\r\n'.encode('utf-8'))

    if execute:
        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            client_socket.send(b'<sh:#> ')
            cmd_buffer = b""
            while b"\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            response = run_command(cmd_buffer.decode('utf-8'))
            client_socket.send(response)


def server_loop(target, port, execute, command, upload_destination):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    print(f'[*] Listening on {target}:{port}')

    while True:
        client_socket, addr = server.accept()
        print(f'[*] Accepted connection from {addr[0]}:{addr[1]}')
        client_handler = threading.Thread(
            target=handle_client,
            args=(client_socket, execute, command, upload_destination)
        )
        client_handler.start()

def client_sender(buffer, target, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))
        if len(buffer):
            client.send(buffer.encode('utf-8'))

        while True:
            recv_len = 1
            response = b""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            print(response.decode('utf-8'))

            buffer = input("")
            buffer += "\n"
            client.send(buffer.encode('utf-8'))
    except Exception as e:
        print(f'[*] Exception! Exiting: {str(e)}')
        client.close()

def main():
    parser = argparse.ArgumentParser(description='Simple TCP server/client with additional features.')
    parser.add_argument('mode', choices=['server', 'client'], help='Run as server or client')
    parser.add_argument('-host', default='127.0.0.1', help='Host to connect/bind to')
    parser.add_argument('-p', type=int, default=9999, help='Port to connect/bind to')
    parser.add_argument('-e', '--execute', help='Execute the given file upon receiving a connection')
    parser.add_argument('-c', '--command', action='store_true', help='Initialize a command shell')
    parser.add_argument('-u', '--upload', help='Upon receiving connection upload a file and write to [destination]')
    args = parser.parse_args()

    if args.mode == 'server':
        server_loop(args.host, args.p, args.execute, args.command, args.upload)
    elif args.mode == 'client':
        buffer = sys.stdin.read()
        client_sender(buffer, args.host, args.p)

if __name__ == '__main__':
    main()
