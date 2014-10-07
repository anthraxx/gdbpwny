
class Breakpoint:
    def __init__(self, gdb, number, address):
        self.gdb = gdb
        self.number = number
        self.address = address

    def ignore(self, count=1):
        return self.gdb.gdb_ignore(self.number, count)

    def disable(self):
        return self.gdb.gdb_disable(self.number)

    def enable(self):
        return self.gdb.gdb_enable(self.number)
