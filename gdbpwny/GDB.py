from subprocess import Popen, PIPE, STDOUT
from sys import stdin, stdout, exit
from binascii import unhexlify
from enum import Enum
from .Breakpoint import Breakpoint
import re


class Signal(Enum):
    SIGHUP    = 1
    SIGINT    = 2
    SIGQUIT   = 3
    SIGILL    = 4
    SIGTRAP   = 5
    SIGABRT   = 6
    SIGBUS    = 7
    SIGFPE    = 8
    SIGKILL   = 9
    SIGUSR1   = 10
    SIGSEGV   = 11
    SIGUSR2   = 12
    SIGPIPE   = 13
    SIGALRM   = 14
    SIGTERM   = 15
    SIGSTKFLT = 16
    SIGCHLD   = 17
    SIGCONT   = 18
    SIGSTOP   = 19
    SIGTSTP   = 20
    SIGTTIN   = 21
    SIGTTOU   = 22
    SIGURG    = 23
    SIGXCPU   = 24
    SIGXFSZ   = 25
    SIGVTALRM = 26
    SIGPROF   = 27
    SIGWINCH  = 28
    SIGIO     = 29
    SIGPWR    = 30


class GDB:
    def __init__(self, program=None, args=[], verbose=0):
        self.prompt = "(gdb) "
        self.verbose = verbose
        self.breakpoints = {}
        self.signal_callbacks = {}
        self.proc = Popen(["gdb", "-n", "-q"], bufsize=0, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        self.read_until_prompt()
        if program: self.file(program)
        if args: self.gdb_set_args(args)

    def read_until(self, search):
        input_buffer = ""
        while not input_buffer.endswith(search):
            input_buffer += self.proc.stdout.read(1)
        return input_buffer

    def parse_gdb_output(self, output):
        for line in output.splitlines():
            if line.startswith("Breakpoint"):
                match = re.compile("Breakpoint (\d+), 0x([\da-f]+) in (.*)").search(line)
                if match:
                    breakpoint_number = match.group(1)
                    address = hex(int(match.group(2), 16))
                    function_information = match.group(3)
                    breakpoint = self.get_breakpoint(breakpoint_number)
                    breakpoint.hit(address, function_information)
            if line.startswith("Program received signal"):
                match = re.compile("Program received signal ([A-Z]+), .*?.\n0x([\da-f]+) in ([^\n]+)\n", re.M).search(output)
                if match:
                    signal = Signal[match.group(1)]
                    address = hex(int(match.group(2), 16))
                    function_information = match.group(3)
                    self.signal_callbacks.get(signal)(self, signal, address, function_information)

    def read_until_prompt(self):
        read_until_prompt = self.read_until(self.prompt)
        if self.verbose >= 1: print("{}".format(read_until_prompt), end="")
        self.parse_gdb_output(read_until_prompt)
        return read_until_prompt

    def print_prompt(self, end=''):
        print("(gdb) ", end=end)

    def execute(self, command):
        self.proc.stdin.write("{}\n".format(command))
        if self.verbose >= 2: print("{}\n".format(command), end="")
        return self.read_until_prompt()

    def breakpoint(self, expression, callback=None):
        output = self.execute("b {}".format(expression))
        match = re.compile('Breakpoint (\d+) at 0x([\da-f]+)').search(output)
        bpnumber = match.group(1)
        address = hex(int(match.group(2), 16))
        b = Breakpoint(self, bpnumber, address, callback)
        self.breakpoints[bpnumber] = b
        return b

    def get_breakpoint(self, number):
        return self.breakpoints.get(number)

    def set_signal_callback(self, signal, callback):
        self.signal_callbacks[signal] = callback

    def gdb_ignore(self, breakpoint, count=0):
        return self.execute("ignore {} {}".format(breakpoint, count))

    def gdb_enable(self, breakpoint):
        return self.execute("enable {}".format(breakpoint))

    def gdb_disable(self, breakpoint):
        return self.execute("disable {}".format(breakpoint))

    def gdb_delete(self, breakpoint):
        return self.execute("delete {}".format(breakpoint))

    def file(self, program):
        return self.execute("file {}".format(program))

    def run(self, args=[]):
        return self.execute("run {}".format(" ".join(args)))

    def start(self, args=[]):
        return self.execute("start {}".format(" ".join(args)))

    def gdb_set_args(self, args=[]):
        return self.execute("set args {}".format(" ".join(args)))

    def gdb_generate_core_file(self, filename=""):
        return self.execute("generate-core-file {}".format(filename))

    def core_file(self, filename=""):
        return self.execute("core-file {}".format(filename))

    def print(self, expression):
        return self.execute("p {}".format(expression))

    def disassemble(self):
        return self.execute("disas")

    def get_stack(self, offset, raw=False):
        output = self.execute("x/x $ebp-{}".format(offset))
        match = re.compile("0x[a-z\d]+.*:\s+0x([a-z\d]+)").search(output).group(1)
        if raw: return unhexlify(match)
        return hex(int(match, 16))

    def set_stack(self, offset, value):
        return self.execute("set {{int}} ($ebp-{}) = {}".format(offset, value))

    def gdb_next(self, count=1):
        return self.execute("next {}".format(count))

    def gdb_nexti(self, count=1):
        return self.execute("nexti {}".format(count))

    def gdb_step(self, count=1):
        return self.execute("step {}".format(count))

    def gdb_stepi(self, count=1):
        return self.execute("stepi {}".format(count))

    def gdb_continue(self):
        return self.execute("c")

    def gdb_interactive(self):
        interactive = True
        print("[+] Entering GDB, press CTRL+D to return...")
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
