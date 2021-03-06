import socket
import threading


class Server:

    def __init__(self, host='', port=9999, proxy_host='localhost', proxy_port=7979):
        self.host = host
        self.port = port

        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()

    def serve_forever(self):
        while True:
            incoming_sock, addr = self.sock.accept()

            try:
                outcoming_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                outcoming_sock.connect((self.proxy_host, self.proxy_port))

                self.run_proxies(outcoming_sock, incoming_sock)

            except OSError as msg:
                print("Could not connect to remote, error: %s" % msg)
                incoming_sock.close()

    def run_proxies(self, out_sock, in_sock):
        proxies = [
            threading.Thread(target=self.handler, args=(out_sock, in_sock)),
            threading.Thread(target=self.handler, args=(in_sock, out_sock)),
        ]

        for proxy in proxies:
            proxy.start()

    @staticmethod
    def handler(recv_sock, send_sock):
        try:
            while True:
                data = recv_sock.recv(1024)
                if not data:
                    send_sock.shutdown(socket.SHUT_RDWR)
                    break
                send_sock.sendall(data)

        finally:
            print("Close connection")
            recv_sock.close()
