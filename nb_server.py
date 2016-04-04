import socket
import threading
import select

N_THREADS = 4


class NBServer:
    def __init__(self, host='', port=9999, proxy_host='localhost', proxy_port=7979):
        self.host = host
        self.port = port

        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()

    def serve_forever(self):
        threads = []
        thread_id = 0
        for i in range(N_THREADS):
            handler = Handler()
            handler.start()
            threads.append(handler)

        while True:
            read, write, err = select.select([self.sock], [], [])

            if self.sock in read:
                incoming_sock, addr = self.sock.accept()

                try:
                    outcoming_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    outcoming_sock.connect((self.proxy_host, self.proxy_port))
                    outcoming_sock.setblocking(False)

                    thread_id = (thread_id + 1) % N_THREADS
                    threads[thread_id].push(incoming_sock, outcoming_sock)

                except OSError as msg:
                    print("Could not connect to remote, error: %s" % msg)
                    incoming_sock.close()


class Handler(threading.Thread):
    def __init__(self):
        super().__init__()
        self.sockets = {}
        self.lock = threading.Lock()

    def run(self):
        while True:
            self.lock.acquire()
            sockets_list = list(self.sockets.keys())
            self.lock.release()

            read, write, err = select.select(sockets_list, [], [], 0.1)

            for fd in read:

                send_sock = None
                recv_sock = None

                try:
                    send_sock = self.sockets[fd]
                    recv_sock = self.sockets[send_sock.fileno()]
                    data = recv_sock.recv(1024)

                    if not data:
                        raise ConnectionResetError()

                    send_sock.send(data)

                except ConnectionResetError:

                    if not send_sock:
                        continue

                    self._del(send_sock)

                except KeyError:
                    continue

    def push(self, recv_sock, send_sock):
        self.lock.acquire()
        self.sockets[recv_sock.fileno()] = send_sock
        self.sockets[send_sock.fileno()] = recv_sock
        self.lock.release()

    def _del(self, socket_):
        paired = self.sockets.pop(socket_.fileno())
        del self.sockets[paired.fileno()]

        socket_.close()
        paired.close()


NBServer().serve_forever()
