import Queue
import inspect
import socket
import ssl
import threading
import time

from smp import SMProtocol


class Server:
    def __init__(self, smprotocol, port, external=False, smp_args=(), ssl_args=None):
        if inspect.isclass(smprotocol):
            self.smprotocol = smprotocol
        else:
            raise ValueError('Specified smp is not a class definition')
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

    def new_client(self, _socket, _address):
        self.new_client_lock.acquire()
        name = str(self.client_counter) + "c"
        _smp = self.smprotocol(_socket, self, name, _address, *self.smp_args)
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

    """
    ;param msg: Message to be sent to targets
    ;param target: a callable that evaluates whether given client should receive the message
    """
    def send_message(self, msg, target=None):
        for client in self.client_smp_dict.values():
            if (target is None or target(client)) and client.is_active:
                client.send_message(msg)

    def run_async(self):
        self.thread.start()

    def run(self):
        self.thread_started = True

        time.sleep(1)

        self.socket.bind((self.host, self.port))
        self.socket.listen(self.backlog)

        while self.is_active:
            try:
                client_sock, address = self.socket.accept()
                if self.ssl_args is not None:
                    client_sock = ssl.wrap_socket(client_sock, server_side=True, **self.ssl_args)
                self.new_client(client_sock, address)
            except:
                pass


class ServerSMProtocol(SMProtocol):
    def __init__(self, sock, server, server_assigned_name, address):
        self.server = server
        self.server_assigned_name = server_assigned_name
        self.address = address
        self.message_queue = Queue.Queue()
        self.message_thread = threading.Thread(target=self.send_message_thread)
        SMProtocol.__init__(self, sock)

    def bind(self):
        SMProtocol.bind(self)
        self.message_thread.start()

    def unbind(self):
        SMProtocol.unbind(self)
        self.message_thread.join()

    def send_message_thread(self):
        while self.is_active:
            try:
                new_message = self.message_queue.get(block=False)
                SMProtocol.send_message(self, new_message)
            except:
                pass

    def send_message(self, msg):
        self.message_queue.put(msg)

    def connection_error(self):
        try:
            del self.server.client_smp_dict[self.server_assigned_name]
        except:
            pass
