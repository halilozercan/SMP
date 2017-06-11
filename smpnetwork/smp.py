import socket
import threading
import time

import smpnetwork
from message import Message


class SMProtocol:
    def __init__(self, sock, hb_interval=5):
        self.sock = sock
        self.receive_thread = threading.Thread(target=self._bind)
        self.__hb_enabled = (hb_interval > 0)
        self.heartbeat_thread = threading.Thread(target=self.heartbeat)
        self.hb_interval = hb_interval
        self.is_active = True
        self.sent_message_counter = 0

    def bind(self):
        self.receive_thread.start()
        if self.__hb_enabled:
            self.heartbeat_thread.start()

    def unbind(self):
        self.is_active = False
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.receive_thread.join()
        if self.__hb_enabled:
            self.heartbeat_thread.join()
        self.sock.close()

    def send_message(self, msg):
        if msg.get_header('content_length') is None:
            msg.set_header('content_length', len(msg.get_body()))

        return smpnetwork.send(msg, self.sock)

    def receive_message(self, message):
        # Should be implemented by subclass
        pass

    def connection_error(self):
        # Should be implemented by subclass
        pass

    def is_connected(self):
        return self.is_active

    def heartbeat(self):
        index = 1
        while self.is_active:
            hb_msg = Message(body="", headers={"HB": str(index)})
            if smpnetwork.send(hb_msg, self.sock):
                time.sleep(self.hb_interval)
                index += 1
            else:
                self.is_active = False
                self.connection_error()

    def _bind(self):
        leftover = ''
        while self.is_active:
            response, leftover = smpnetwork.receive(self.sock, leftover=leftover)
            if response.is_successful():
                string = response.getData()
                try:
                    received_message = Message.from_str(string)
                except:
                    continue

                if received_message.get_header('HB') is not None:
                    # Simple heartbeat. Al iz wel
                    continue

                self.receive_message(received_message)

            elif response.getData() != 'timeout' or (response.getData() == 'timeout' and self.__hb_enabled):
                self.sock.close()
                self.is_active = False
                self.connection_error()
