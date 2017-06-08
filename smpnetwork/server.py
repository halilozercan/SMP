import socket
import threading
import time
import ssl

import tools
from smp import SMProtocol


class Server:
    def __init__(self, smprotocol, port, external=False, smp_args=(), ssl_args=None):
        self.smprotocol = smprotocol
        self.port = port
        self.external = external
        self.ssl_args = ssl_args

        self.backlog = 20

        if external:
            self.host = '0.0.0.0'
        else:
            self.host = 'localhost'

        self.smp_args = smp_args
        self.is_active = True
        self.thread = threading.Thread(target=self.run)
        self.client_smp_dict = {}
        self.client_counter = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)
        self.thread_started = False

        self.new_client_lock = threading.Lock()

    def new_client(self, _socket):
        self.new_client_lock.acquire()
        name = str(self.client_counter) + "_client"
        _smp = self.smprotocol(_socket, self, name, *self.smp_args)
        _smp.bind()
        self.client_smp_dict[name] = _smp
        self.client_counter += 1

        self.new_client_lock.release()

    def stop(self):
        self.is_active = False
        for smp in self.client_smp_dict.values():
            smp.unbind()
        self.socket.close()
        if self.thread_started:
            self.thread.join(timeout=2)
        return True

    def send_message(self, body, headers, target=None):
        for smp in self.client_smp_dict.values():
            if (target is None or target == smp.name) and smp.is_active:
                smp.send_message(body, headers)

    def run_async(self):
        self.thread.start()

    def run(self):
        self.thread_started = True

        time.sleep(1)

        self.socket.bind((self.host, self.port))
        self.socket.listen(self.backlog)

        tools.log("Started server at" + str(self.port))

        while self.is_active:
            try:
                client_sock, address = self.socket.accept()
                if self.ssl_args is not None:
                    client_sock = ssl.wrap_socket(client_sock, server_side=True, **self.ssl_args)
                self.new_client(client_sock)
            except Exception as exc:
                tools.log('Networking error: ' + str(self.port))
                tools.log(exc)


class ServerSMProtocol(SMProtocol):
    def __init__(self, sock, server, server_assigned_name):
        self.server = server
        self.server_assigned_name = server_assigned_name
        SMProtocol.__init__(self, sock)

    def connection_error(self):
        try:
            del self.server.client_smp_dict[self.server_assigned_name]
        except:
            tools.log("Could not delete connection from server pool")
