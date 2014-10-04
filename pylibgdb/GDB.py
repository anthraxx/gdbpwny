from subprocess import Popen, PIPE, STDOUT
from sys import stdin, stdout, exit
from binascii import unhexlify
import re

interactive = False
class GDB:
    def __init__(self, program):
        self.prompt = "(gdb) "
        self.proc = Popen(["gdb", "-n", "-q", program], bufsize=0, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        self.output()

    def read_until(self, search):
        input_buffer = ""
        while not input_buffer.endswith(search):
            input_buffer += self.proc.stdout.read(1)
        return input_buffer

    def output(self):
        output = self.read_until(self.prompt)
        print("{}".format(output), end="")
        return output

    def print_prompt(self, end=''):
        print("(gdb) ", end=end)

    def execute(self, command):
        self.proc.stdin.write("{0}\n".format(command))
        print("{}\n".format(command), end="")

    def breakpoint(self, expression):
        self.execute("b {0}".format(expression))
        self.output()

    def gdb_ignore(self, breakpoint, count=0):
        self.execute("ignore {} {}".format(breakpoint, count))
        self.output()

    def run(self, args=[]):
        self.execute("run {}".format(" ".join(args)))
        self.output()

    def print(self, expression):
        self.execute("p {}".format(expression))
        self.output()
    
    def disassemble(self):
        self.execute("disas")
        self.output()

    def get_stack(self, offset, raw=False):
        self.execute("x/x $ebp-{}".format(offset))
        output = self.output()
        match = re.compile("0x[a-z0-9]+.*:\s+0x([a-z0-9]+)").search(output).group(1)
        if raw: return unhexlify(match)
        return hex(int(match, 16))

    def set_stack(self, offset, value):
        self.execute("set {{int}} ($ebp-{}) = {}".format(offset, value))
        self.output()
    
    def gdb_continue(self):
        self.execute("c")
        self.output()

    def gdb_interactive(self):
        global interactive
        interactive = True
        print("\n[+] Entering GDB, press CTRL+D to return...")
        self.print_prompt()
        while interactive:
            try:
                self.proc.stdin.write("{}\n".format(input()))
                self.output()
            except EOFError:
                interactive = False
                print("")
            except KeyboardInterrupt:
                self.output()
