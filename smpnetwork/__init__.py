import socket

import tools
from message import Message
from response import Response

MAX_MESSAGE_SIZE = 1024


def receive(sock, **kwargs):
    """
    Receives a socket message from one time. This is not a SMP message.
    :param sock: Socket
    :param kwargs: 
    :return:
    """
    args = dict(
        timeout=-1
    )
    args.update(kwargs)

    if args['timeout'] != -1:
        sock.settimeout(args['timeout'])
    else:
        sock.settimeout(10)

    try:
        string = sock.recv(MAX_MESSAGE_SIZE)
        length = int(string[:string.index(":")])
        string = string[string.index(":") + 1:]
        while len(string) < length:
            string += sock.recv(MAX_MESSAGE_SIZE)
    except socket.timeout:
        # Timed out
        return Response(False, 'Receive timed out')

    if string == '':
        # it is eof. Socket is fucked up
        return Response(False, "Connection closed")

    return Response(True, string)


def send(body, headers, sock):
    _msg = Message(header=headers, body=body)

    msg = str(_msg)
    sent = 0
    total = 0

    if isinstance(msg, str):
        try:
            msg = str(len(msg)) + ":" + msg
            total = len(msg)
            sent += sock.send(msg)
        except:
            tools.log('Peer died')
            return False
    else:
        for part in msg:
            total += len(part)
            try:
                sent += sock.send(part)
            except:
                tools.log('Peer died')
                return False

    return sent == total


def connect(host='localhost', port=3699, ssl_args=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(5)
    if ssl_args is not None:
        import ssl
        s = ssl.wrap_socket(s, **ssl_args)
    try:
        s.connect((host, port))
        return s
    except:
        return None
