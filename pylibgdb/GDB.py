from subprocess import Popen, PIPE, STDOUT
from sys import stdin, stdout, exit
import pexpect

interactive = False
class GDB:
    def __init__(self, program):
        self.proc = Popen(["gdb", "-n", "-q", program], bufsize=0, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        
        self.child = pexpect.spawn('gdb -n -q {}'.format(program))
        self.prompt = "(gdb) "
        self.output()

    def read_until(self, search):
        input_buffer = ""
        while not input_buffer.endswith(search):
            input_buffer += self.proc.stdout.read(1)
        return input_buffer

    def output(self):
        print("{0}".format(self.read_until(self.prompt)), end="")

    def execute(self, command):
        self.proc.stdin.write("{0}\n".format(command))
        print("{0}\n".format(command), end="")

    def breakpoint(self, expression):
        self.execute("b {0}".format(expression))
        self.output()

    def run(self):
        self.execute("r")
        self.output()

    def print(self, expression):
        self.execute("p {}".format(expression))
        self.output()
    
    def disassemble(self):
        self.execute("disas")
        self.output()

    def get_stack(self, offset):
        self.execute("x/wx $ebp-{}".format(offset))
        self.output()

    def set_stack(self, offset, value):
        self.execute("set {{int}} ($ebp-{}) = {}".format(offset, value))
        self.output()
    
    def gdb_continue(self):
        self.execute("c")
        self.output()

    def gdb_interactive(self):
        global interactive
        interactive = True
        while interactive:
            print("[*] Reading input..")
            try:
                self.proc.stdin.write("{}\n".format(input()))
                print("[*] Input read...")
                self.output()
            except EOFError:
                interactive = False
            except KeyboardInterrupt:
                self.output()
