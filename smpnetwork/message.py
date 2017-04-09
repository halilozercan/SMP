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
        result += "\n"
        result += self.body
        result += "\n%end_body%\n"
        return result

    def package(self):
        str_rep = str(self)
        """
        if len(str_rep) > network.MAX_MESSAGE_SIZE:
            if "id" in self.headers:
                prefix = ""
                prefix += json.dumps(self.headers)
                prefix += "\n"

                body_parts = self.body + "\n%end_body%\n"
                body_parts = tools.split_size(
                    body_parts, network.MAX_MESSAGE_SIZE - len(prefix))
                parts = []
                for body_part in body_parts:
                    part = prefix + body_part
                    parts.append(part)
                return parts
            else:
                raise RuntimeError("A multipart message cannot be packaged without ID header field")
        else:
            return str_rep
        """
        return str_rep