from subprocess import Popen, PIPE, STDOUT
from sys import stdin, stdout, exit
from binascii import unhexlify
import re

interactive = False
class GDB:
    def __init__(self, program, verbose=0):
        self.prompt = "(gdb) "
        self.verbose = verbose
        self.proc = Popen(["gdb", "-n", "-q", program], bufsize=0, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        self.read_until_prompt()

    def read_until(self, search):
        input_buffer = ""
        while not input_buffer.endswith(search):
            input_buffer += self.proc.stdout.read(1)
        return input_buffer

    def read_until_prompt(self):
        read_until_prompt = self.read_until(self.prompt)
        if self.verbose >= 1: print("{}".format(read_until_prompt), end="")
        return read_until_prompt

    def print_prompt(self, end=''):
        print("(gdb) ", end=end)

    def execute(self, command):
        self.proc.stdin.write("{0}\n".format(command))
        if self.verbose >= 2: print("{}\n".format(command), end="")
        return self.read_until_prompt()

    def breakpoint(self, expression):
        return self.execute("b {0}".format(expression))

    def gdb_ignore(self, breakpoint, count=0):
        return self.execute("ignore {} {}".format(breakpoint, count))

    def run(self, args=[]):
        return self.execute("run {}".format(" ".join(args)))

    def print(self, expression):
        return self.execute("p {}".format(expression))
    
    def disassemble(self):
        return self.execute("disas")

    def get_stack(self, offset, raw=False):
        output = self.execute("x/x $ebp-{}".format(offset))
        match = re.compile("0x[a-z0-9]+.*:\s+0x([a-z0-9]+)").search(output).group(1)
        if raw: return unhexlify(match)
        return hex(int(match, 16))

    def set_stack(self, offset, value):
        return self.execute("set {{int}} ($ebp-{}) = {}".format(offset, value))
    
    def gdb_continue(self):
        return self.execute("c")

    def gdb_interactive(self):
        global interactive
        interactive = True
        print("\n[+] Entering GDB, press CTRL+D to return...")
        self.print_prompt()
        verbose_old = self.verbose
        self.verbose = 2
        while interactive:
            try:
                self.proc.stdin.write("{}\n".format(input()))
                self.read_until_prompt()
            except EOFError:
                interactive = False
                print("")
            except KeyboardInterrupt:
                self.read_until_prompt()
        self.verbose = verbose_old
