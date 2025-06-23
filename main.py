MEMORY_SIZE = 4096 #4KB Memory
memory = bytearray(MEMORY_SIZE)
registers = [0] * 32  # 32 registers
pc = 0

def load_program(path):
    with open(path, "rb") as f:
        program = f.read()
        memory[0:len(program)] = program

def run():
    global pc
    while pc < len(memory):
        instr = int.from_bytes(memory[pc:pc+4], byteorder='little')
        pc += 4
        execute(instr)

def sign_extend(value, bits) :
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

def execute(instr):
    opcode = instr & 0x7f

    if (opcode == 0x33):  # R-type instruction
        rd = (instr >> 7) & 0x1f
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1f
        rs2 = (instr >> 20) & 0x1f
        funct7 = (instr >> 25) & 0x7f
        if (funct3 == 0x0) :
            if (funct7 == 0x00) : #add
                registers[rd] = (registers[rs1] + registers[rs2]) & 0xffffffff
            elif (funct7 == 0x20) : #sub
                registers[rd] = (registers[rs1] - registers[rs2]) & 0xffffffff
        elif (funct3 == 0x4) : #xor
            registers[rd] = (registers[rs1] ^ registers[rs2]) & 0xffffffff
        elif (funct3 == 0x6) : #or
            registers[rd] = (registers[rs1] | registers[rs2]) & 0xffffffff
        elif (funct3 == 0x7) : #and
            registers[rd] = (registers[rs1] & registers[rs2]) & 0xffffffff
        elif (funct3 == 0x1) : #sll
            registers[rd] = (registers[rs1] << (registers[rs2] & 0x1f)) & 0xffffffff
        elif (funct3 == 0x5) :
            if (funct7 == 0x00) : #srl
                registers[rd] = (registers[rs1] >> (registers[rs2] & 0x1f)) & 0xffffffff
            elif (funct7 == 0x20) : #sra
                val = registers[rs1] & 0xffffffff
                if val & 0x80000000:
                    registers[rd] = (val >> (registers[rs2] & 0x1f)) | (0xffffffff << (32 - (registers[rs2] & 0x1f))) & 0xffffffff
                else:
                    registers[rd] = val >> (registers[rs2] & 0x1f)
        elif (funct3 == 0x2) : #slt
            registers[rd] = 1 if sign_extend(registers[rs1], 32) < sign_extend(registers[rs2], 32) else 0
        elif (funct3 == 0x3) : #sltu
            registers[rd] = 1 if (registers[rs1] & 0xffffffff) < (registers[rs2] & 0xffffffff) else 0
         

    elif (opcode == 0x13) : #I-type instruction
        rd = (instr >> 7) & 0x1f
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1f
        imm = (instr >> 20) & 0xfff
        imm = sign_extend(imm, 12)
        if (funct3 == 0x0) :
            registers[rd] = (registers[rs1] + imm) & 0xffffffff
    elif (opcode == 0x73) :
        global pc
        print("ECALL, ending execution")
        pc = len(memory)

load_program("test.bin")
run()

print("x1 =", registers[1])    # 15
print("x2 =", registers[2])    # 10
print("x3 =", hex(registers[3]))  # 0xFFFFFFFF (−1)
print("x4 =", registers[4])    # 1
print("x5 =", registers[5])    # 25
print("x6 =", registers[6])    # 5
print("x7 =", registers[7])    # 11
print("x8 =", registers[8])    # 11
print("x9 =", registers[9])    # 0
print("x10 =", registers[10])  # 1024
print("x11 =", hex(registers[11])) # 0x7FFFFFFF
print("x12 =", hex(registers[12])) # 0xFFFFFFFF
print("x13 =", registers[13])  # 1
print("x14 =", registers[14])  # 0