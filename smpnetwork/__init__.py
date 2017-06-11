import socket

from message import Message
from response import Response

MAX_MESSAGE_SIZE = 1024


def receive(sock, **kwargs):
    """
    Receives a socket message one time. This is not a SMP message.
    :param sock: Socket
    :param kwargs: 
    :return:
    """
    args = dict(
        timeout=-1,
        leftover=''
    )
    args.update(kwargs)

    if args['timeout'] != -1:
        sock.settimeout(args['timeout'])
    else:
        sock.settimeout(10)

    try:
        string = args['leftover']
        while string == '':
            string += sock.recv(MAX_MESSAGE_SIZE)

        while string.find(':') < 0:
            string += sock.recv(MAX_MESSAGE_SIZE)

        sep_loc = string.find(":")
        length = int(string[:sep_loc])
        string = string[sep_loc + 1:]

        while len(string) < length:
            string += sock.recv(MAX_MESSAGE_SIZE)

        received_string = string[:length]
        leftover = string[length:]
        return Response(True, received_string), leftover

    except socket.timeout:
        # Timed out
        return Response(False, 'timeout')


def send(_msg, sock):
    msg = str(_msg)

    try:
        msg = str(len(msg)) + ":" + msg
        sent = sock.send(msg)
    except:
        return False

    return sent == len(msg)


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
