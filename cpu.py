"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.FL = [0] * 8
        self.flags = {"L": 5, "G": 6, "E": 7}
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.HLT = 0b00000001
        self.MUL = 0b10100010
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.CMP = 0b10100111
        self.JMP = 0b01010100
        self.JEQ = 0b01010101
        self.JNE = 0b01010110
        self.reg[7] = 0xF4

    def ram_read(self, address):
        return self.reg[address]

    def ram_write(self, value, address):
        self.reg[address] = value

    def load(self):
        """Load a program into memory."""
        program_file = sys.argv[1]

        program = []

        with open(program_file) as file:
            for line in file:
                line_list = line.split("#")
                binary_str = line_list[0].strip()
                if "0" in binary_str or "1" in binary_str:
                    binary = int(binary_str, 2)
                    program.append(binary)

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.reg[i], end="")

        print()

    def run(self):
        """Run the CPU."""
        # self.load()

        running = True
        pc = 0

        while running:
            cmd = self.ram[pc]

            if cmd == self.HLT:
                running = False
            elif cmd == self.LDI:
                register_index = self.ram[pc + 1]
                register_value = self.ram[pc + 2]
                self.ram_write(address=register_index, value=register_value)
                pc += 3
            elif cmd == self.PRN:
                address = self.ram[pc + 1]
                value = self.ram_read(address)
                print(value)
                pc += 2
            elif cmd == self.MUL:
                num1 = self.ram_read(self.ram[pc + 1])
                num2 = self.ram_read(self.ram[pc + 2])

                print(num1 * num2)
                pc += 3

            elif cmd == self.PUSH:
                self.reg[7] -= 1

                address = self.ram[pc + 1]
                value = self.ram_read(address)

                SP = self.reg[7]
                self.ram[SP] = value

                pc += 2
            elif cmd == self.POP:
                SP = self.reg[7]
                value = self.ram[SP]
                target_address = self.ram[pc + 1]
                self.reg[target_address] = value

                self.reg[7] += 1

                pc += 2

            elif cmd == self.CMP:
                registerA = self.ram_read(self.ram[pc + 1])
                registerB = self.ram_read(self.ram[pc + 2])

                self.FL[self.flags["E"]] = 1 if registerA == registerB else 0
                self.FL[self.flags["L"]] = 1 if registerA < registerB else 0
                self.FL[self.flags["G"]] = 1 if registerA > registerB else 0

                pc += 3

            elif cmd == self.JMP:
                value = self.ram_read(self.ram[pc + 1])

                pc = value

            elif cmd == self.JEQ:
                value = self.ram_read(self.ram[pc + 1])

                if self.FL[self.flags["E"]] == 1:
                    pc = value
                else:
                    pc += 2

            elif cmd == self.JNE:
                value = self.ram_read(self.ram[pc + 1])

                if self.FL[self.flags["E"]] != 1:
                    pc = value
                else:
                    pc += 2

