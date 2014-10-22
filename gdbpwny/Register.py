
class Register(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return "<register name={} value={}>".format(self.name, self.value)

    def __repr__(self):
        return str(self)


class RegisterSet(dict):
    pass
