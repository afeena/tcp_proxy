import unittest
import socket
from server import Server
from unittest.mock import Mock, patch, MagicMock


class TestServer(unittest.TestCase):

    def test_serve(self):

        sock_mock = Mock()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        t = ('127.0.0.1',5568)
        attrs = {'socket.return_value':sock_mock, 'accept.side_effect':[(s,t),(s,t),KeyboardInterrupt],'connect.side_effect':[None, OSError]}
        sock_mock.configure_mock(**attrs)

        with patch('server.socket',sock_mock):
            srv = Server()
            srv.run_proxies = MagicMock(return_value = None)
            try:
                srv.serve_forever()

            except KeyboardInterrupt:
                pass

            sock_mock.connect.assert_called_with(('localhost', 7979))



    def test_handle_is_forwarding_correct(self):
        send_mock = Mock()
        recv_mock = Mock()
        recv_mock.recv.side_effect = [b'test', None]

        Server.handler(recv_mock, send_mock)

        assert recv_mock.recv.called
        send_mock.sendall.assert_called_once_with(b'test')
        assert recv_mock.close.called

