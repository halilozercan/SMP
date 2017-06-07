import json


class Message:
    def __init__(self, header=None, body=""):
        if header is None:
            header = {}
        self.headers = header
        self.body = body

    def set_header(self, key, value):
        self.headers[key] = value

    def get_header(self, key):
        if key in self.headers.keys():
            return self.headers[key]
        else:
            return None

    def set_body(self, body):
        self.body = body

    def add_body(self, b):
        self.body += b

    def get_body(self):
        return self.body

    def __str__(self):
        result = ""
        result += json.dumps(self.headers)
        result += '\n'
        result += self.body
        result += '\x10'
        return result