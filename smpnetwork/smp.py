import json
import socket
import threading
import time
from message import Message
import smpnetwork
from smpnetwork import tools


class SMProtocol:
    def __init__(self, sock, hb_interval=5):
        self.sock = sock
        self.receive_thread = threading.Thread(target=self._bind)
        self.heartbeat_thread = threading.Thread(target=self.heartbeat)
        self.is_active = True
        self._messages = {}
        self.sent_message_counter = 0
        self.hb_interval = hb_interval

    def bind(self):
        self.receive_thread.start()
        self.heartbeat_thread.start()

    def unbind(self):
        self.is_active = False
        self.receive_thread.join(timeout=3)
        self.heartbeat_thread.join(timeout=3)
        self.sock.close()

    def send_message(self, body, headers):
        if "id" not in headers:
            headers["id"] = "message_" + str(self.sent_message_counter)

        if "content_length" not in headers:
            headers["content_length"] = len(body)

        return smpnetwork.send(body, headers, self.sock)

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
            if smpnetwork.send("", {"HB": str(index)}, self.sock):
                time.sleep(self.hb_interval)
                index += 1
            else:
                self.is_active = False
                self.connection_error()

    def _bind(self):
        def strip_eof(message):
            body = message.get_body()
            if body[-1] == '\x10':
                body = body[:-1]
                message.set_body(body)
                return message
            else:
                return None

        while self.is_active:
            response = smpnetwork.receive(self.sock)
            if response.is_successful():
                string = response.getData()
                try:
                    header_end_index = string.index("\n")
                    header_str = string[:header_end_index]
                    body_str = string[header_end_index + 1:]
                except:
                    tools.log("Could not partition received string")
                    continue

                try:
                    header_dict = json.loads(header_str)
                except:
                    tools.log("Header could not be parsed")
                    continue

                if "HB" in header_dict:
                    # Simple heartbeat. Al iz wel
                    continue

                if "id" in header_dict:
                    # Can be part of a multipart message
                    if header_dict["id"] in self._messages:
                        earlier_message = self._messages[header_dict["id"]]
                        earlier_message.add_body(body_str)
                    else:
                        msg = Message(header_dict, body_str)
                        self._messages[header_dict["id"]] = msg
                    # Check whether this message is finally complete

                    current_message = self._messages[header_dict["id"]]
                else:
                    # Message should(must) not be multipart
                    current_message = Message(header_dict, body_str)

                stripped = strip_eof(current_message)
                if stripped is not None:
                    current_message = stripped
                    if "id" in header_dict:
                        del self._messages[header_dict["id"]]
                    self.receive_message(current_message)

            else:
                # Receive did not complete well. Something is wrong with socket.
                # We decide to close it after printing out reason
                tools.log(response.getData())
                self.sock.close()
                self.is_active = False
                self.connection_error()
