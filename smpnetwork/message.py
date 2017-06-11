import json


class Message:
    def __init__(self, headers=None, body=""):
        if headers is None:
            headers = {}
        self.headers = headers
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

    def __repr__(self):
        return self.body

    @staticmethod
    def from_str(string):
        header_end_index = string.index("\n")
        header_str = string[:header_end_index]
        body_str = string[header_end_index + 1:]

        header_dict = json.loads(header_str)

        if body_str[-1] == '\x10':
            body_str = body_str[:-1]
        else:
            raise ValueError('Body does not end with marking character')

        return Message(headers=header_dict, body=body_str)