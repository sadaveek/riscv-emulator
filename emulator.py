MEMORY_SIZE = 4096 #4KB Memory
memory = bytearray(MEMORY_SIZE)
rg = [0] * 32  # 32 registers
pc = 0

def load_program(path):
    with open(path, "rb") as f:
        program = f.read()
        memory[0:len(program)] = program

def run():
    global pc
    while pc < len(memory):
        instr = int.from_bytes(memory[pc:pc+4], byteorder='little')
        execute(instr)

def sign_extend(value, bits) :
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

def debugger() :
    print("\nEntered Debugger - type 'help' for options.")
    while True:
        cmd = input(">>> ").strip().lower()
        if cmd == "help":
            print("Available commands:")
            print(" regs    →   show all registers")
            print(" mem [addr]    →   show 16 bytes from memory at [addr]")
            print(" pc    →   show current program counter")
            print(" cont    →   continue execution")
            print(" step    →   one step of instruction")
            print(" exit    →   exit emulator")
        elif cmd == "regs":
            for i in range(32):
                print(f"x{i} = {rg[i]}")
        elif cmd.startswith("mem"):
            try:
                addr = int(cmd.split()[1], 0)
                dump_memory(addr)
            except:
                print("Invalid address.")
        elif cmd == "pc":
            print(f"PC = {pc:#x}")
        elif cmd == "cont":
            break
        elif cmd == "step":
            instr = int.from_bytes(memory[pc:pc+4], byteorder='little')
            execute(instr)
            print(f"Stepped one instruction to PC = {pc:#x}")
        elif cmd == "exit":
            print("Exiting emulator...")
            exit()
        else:
            print("Command not recognized.")

def dump_memory(addr, length=16):
    print(f"Memory at {hex(addr)}:")
    for i in range(0, length, 4):
        chunk = memory[addr+i:addr+i+4]
        val = int.from_bytes(chunk, byteorder='little')
        print(f" {hex(addr+i)}: {val:08x}")

def execute(instr):
    global pc
    old_pc = pc
    opcode = instr & 0x7f

    if (opcode == 0x33):  # R-type instruction
        rd = (instr >> 7) & 0x1f
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1f
        rs2 = (instr >> 20) & 0x1f
        funct7 = (instr >> 25) & 0x7f
        if (funct3 == 0x0) :
            if (funct7 == 0x00) : #add
                rg[rd] = (rg[rs1] + rg[rs2]) & 0xffffffff
            elif (funct7 == 0x20) : #sub
                rg[rd] = (rg[rs1] - rg[rs2]) & 0xffffffff
        elif (funct3 == 0x4) : #xor
            rg[rd] = (rg[rs1] ^ rg[rs2]) & 0xffffffff
        elif (funct3 == 0x6) : #or
            rg[rd] = (rg[rs1] | rg[rs2]) & 0xffffffff
        elif (funct3 == 0x7) : #and
            rg[rd] = (rg[rs1] & rg[rs2]) & 0xffffffff
        elif (funct3 == 0x1) : #sll
            rg[rd] = (rg[rs1] << (rg[rs2] & 0x1f)) & 0xffffffff
        elif (funct3 == 0x5) :
            if (funct7 == 0x00) : #srl
                rg[rd] = (rg[rs1] >> (rg[rs2] & 0x1f)) & 0xffffffff
            elif (funct7 == 0x20) : #sra
                val = rg[rs1] & 0xffffffff
                if val & 0x80000000:
                    rg[rd] = (val >> (rg[rs2] & 0x1f)) | (0xffffffff << (32 - (rg[rs2] & 0x1f))) & 0xffffffff
                else:
                    rg[rd] = val >> (rg[rs2] & 0x1f)
        elif (funct3 == 0x2) : #slt
            rg[rd] = 1 if sign_extend(rg[rs1], 32) < sign_extend(rg[rs2], 32) else 0
        elif (funct3 == 0x3) : #sltu
            rg[rd] = 1 if (rg[rs1] & 0xffffffff) < (rg[rs2] & 0xffffffff) else 0

    elif (opcode == 0x13) : #I-type operation
        rd = (instr >> 7) & 0x1f
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1f
        imm = (instr >> 20) & 0xfff
        imm = sign_extend(imm, 12)
        if (funct3 == 0x0) : #addi
            rg[rd] = (rg[rs1] + imm) & 0xffffffff
        elif (funct3 == 0x4) : #xori
            rg[rd] = (rg[rs1] ^ imm)
        elif (funct3 == 0x6) : #ori
            rg[rd] = (rg[rs1] | imm)
        elif (funct3 == 0x7) : #andi
            rg[rd] = rg[rs1] & imm
        elif (funct3 == 0x1) : #slli
            rg[rd] = (rg[rs1] << (imm & 0x1f)) & 0xffffffff
        elif (funct3 == 0x5) :
            if (imm >> 5 == 0x00) : #srli
                rg[rd] = (rg[rs1] >> (imm & 0x1f)) & 0xffffffff
            elif (imm >> 5 == 0x20) : #srai
                val = rg[rs1] & 0xffffffff
                if val & 0x80000000:
                    rg[rd] = (val >> (imm & 0x1f)) | (0xffffffff << (32 - (imm & 0x1f))) & 0xffffffff
                else:
                    rg[rd] = val >> (imm & 0x1f)
        elif (funct3 == 0x2) : #slti
            rg[rd] = 1 if sign_extend(rg[rs1], 32) < imm else 0
        elif (funct3 == 0x3) : #sltiu
            rg[rd] = 1 if (rg[rs1] & 0xffffffff) < (imm & 0xffffffff) else 0
    
    elif (opcode == 0x3) : #I-type load
        rd = (instr >> 7) & 0x1f
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1f
        imm = (instr >> 20) & 0xfff
        imm = sign_extend(imm, 12)
        address = rg[rs1] + imm
        if (funct3 == 0x0) : #lb
            rg[rd] = sign_extend(memory[rg[rs1] + imm], 8)
        elif (funct3 == 0x1) : #lh
            val = int.from_bytes(memory[address:address + 2], "little")
            rg[rd] = sign_extend(val, 16)
        elif (funct3 == 0x2) : #lw
            val = int.from_bytes(memory[address:address + 4], "little")
            rg[rd] = sign_extend(val, 32)
        elif (funct3 == 0x4) : #lbu
            rg[rd] = (memory[rg[rs1] + imm]) & 0xff
        elif (funct3 == 0x5) : #lhu
            val = int.from_bytes(memory[address:address + 2], "little")
            rg[rd] = val & 0xffff
    
    elif (opcode == 0x23) :  #S-type instructions
        imm_bot = (instr >> 7) & 0x1f
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1f
        rs2 = (instr >> 20) & 0x1f
        imm_top = (instr >> 25) & 0x7f
        imm = (imm_top << 5) | imm_bot
        imm = sign_extend(imm, 12)
        address = rg[rs1] + imm
        if (funct3 == 0x0) : #sb
            memory[address] = rg[rs2] & 0xff
        elif (funct3 == 0x1) : #sh
            memory[address:address + 2] = int.to_bytes(rg[rs2] & 0xffff, 2, "little")
        elif (funct3 == 0x2) : #sw
            memory[address:address + 4] = int.to_bytes(rg[rs2] & 0xffffffff, 4, "little")

    elif (opcode == 0x63) : #B-type instructions
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1f
        rs2 = (instr >> 20) & 0x1f
        imm = ((instr >> 8) & 0xf) << 1
        imm |= ((instr >> 25) & 0x3f) << 5
        imm |= ((instr >> 7) & 0x1) << 11
        imm |= ((instr >> 31 & 0x1)) << 12
        imm = sign_extend(imm, 13)
        if (funct3 == 0x0) : #beq
            pc = pc + imm if rg[rs1] == rg[rs2] else pc
        elif (funct3 == 0x1) : #bne
            pc = pc + imm if rg[rs1] != rg[rs2] else pc
        elif (funct3 == 0x4) : #blt
            pc = pc + imm if sign_extend(rg[rs1], 32) < sign_extend(rg[rs2], 32) else pc
        elif (funct3 == 0x5) : #bge
            pc = pc + imm if sign_extend(rg[rs1], 32) >= sign_extend(rg[rs2], 32) else pc
        elif (funct3 == 0x6) : #bltu
            pc = pc + imm if rg[rs1] & 0xffffffff < rg[rs2] & 0xffffffff else pc
        elif (funct3 == 0x7) : #bgeu
            pc = pc + imm if rg[rs1] & 0xffffffff >= rg[rs2] & 0xffffffff else pc

    elif (opcode == 0x6f) : #jal (J-type)
        rd = (instr >> 7) & 0x1f
        imm = ((instr >> 20) & 0x3ff) << 1
        imm |= ((instr >> 19) & 0x1) << 11
        imm |= ((instr >> 12) & 0xff) << 12
        imm |= ((instr >> 31) & 0x1) << 20
        imm = sign_extend(imm, 21)
        rg[rd] = pc + 4
        pc += imm
    
    elif (opcode == 0x67) : #jalr (I-type)
        rd = (instr >> 7) & 0x1f
        funct3 = (instr >> 12) & 0x7
        rs1 = (instr >> 15) & 0x1f
        imm = (instr >> 20) & 0xfff
        imm = sign_extend(imm, 12)
        if (funct3 == 0x0) :
            rg[rd] = pc + 4
            pc = (rg[rs1] + imm) & 0xfffffffe

    elif (opcode == 0x37):  # lui (U-type)
        rd = (instr >> 7) & 0x1f
        imm = (instr >> 12) & 0xfffff
        rg[rd] = imm << 12

    elif (opcode == 0x17):  # auipc (U-type)
        rd = (instr >> 7) & 0x1f
        imm = (instr >> 12) & 0xfffff
        rg[rd] = pc + (imm << 12)

    elif (opcode == 0x73) : #Environment call / break
        imm = (instr >> 20) & 0xfff
        if (imm == 0x0) :
            print("ECALL, ending execution")
            pc = len(memory)
        elif (imm == 0x1) :
            print("EBREAK")
            pc += 4
            debugger()
    if pc == old_pc:
        pc += 4
    rg[0] = 0


load_program("test.bin")
run()

for i in range(32):
    print(f"x{i} = {rg[i]}")