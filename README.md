# tcp_proxy

server.py implements proxy, which use sockets in blocking mode, that's why it creates a pair of threads for every connection.
nb_server.py implements proxy, which use sockets in non-blocking mode, it creates N threads for connection load balancing.
