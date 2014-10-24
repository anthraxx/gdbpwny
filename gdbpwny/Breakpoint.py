
class Breakpoint(object):
    def __init__(self, gdb, number, address, callback=None):
        self.gdb = gdb
        self.number = number
        self.address = address
        self.callback = callback

    def ignore(self, count=1):
        return self.gdb.gdb_ignore(self.number, count)

    def enable(self):
        return self.gdb.gdb_enable(self.number)

    def disable(self):
        return self.gdb.gdb_disable(self.number)

    def delete(self):
        return self.gdb.gdb_delete(self.number)

    def hit(self, address, function_information):
        if self.callback:
            self.callback(self.gdb, self.number, address, function_information)
