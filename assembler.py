import os, re

REGISTER_MAP = {f'x{i}': i for i in range(32)}
REGISTER_MAP.update({
    'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
    't0': 5, 't1': 6, 't2': 7,
    's0': 8, 'fp': 8, 's1': 9,
    'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
    's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27,
    't3': 28, 't4': 29, 't5': 30, 't6': 31
})

INSTRUCTION_SET = {
    # R-type
    'add':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b000, 'funct7': 0b0000000},
    'sub':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b000, 'funct7': 0b0100000},
    'sll':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b001, 'funct7': 0b0000000},
    'slt':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b010, 'funct7': 0b0000000},
    'sltu': {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b011, 'funct7': 0b0000000},
    'xor':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b100, 'funct7': 0b0000000},
    'srl':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b101, 'funct7': 0b0000000},
    'sra':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b101, 'funct7': 0b0100000},
    'or':   {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b110, 'funct7': 0b0000000},
    'and':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b111, 'funct7': 0b0000000},
    # I-type
    'addi': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b000},
    'slti': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b010},
    'sltiu':{'type': 'I', 'opcode': 0b0010011, 'funct3': 0b011},
    'xori': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b100},
    'ori':  {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b110},
    'andi': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b111},
    'slli': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b001, 'funct7': 0b0000000},
    'srli': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b101, 'funct7': 0b0000000},
    'srai': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b101, 'funct7': 0b0100000},
    'jalr': {'type': 'I', 'opcode': 0b1100111, 'funct3': 0b000},
    'lb':   {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b000},
    'lh':   {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b001},
    'lw':   {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b010},
    'lbu':  {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b100},
    'lhu':  {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b101},
    # S-type
    'sb':   {'type': 'S', 'opcode': 0b0100011, 'funct3': 0b000},
    'sh':   {'type': 'S', 'opcode': 0b0100011, 'funct3': 0b001},
    'sw':   {'type': 'S', 'opcode': 0b0100011, 'funct3': 0b010},
    # B-type
    'beq':  {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b000},
    'bne':  {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b001},
    'blt':  {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b100},
    'bge':  {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b101},
    'bltu': {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b110},
    'bgeu': {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b111},
    # U-type
    'lui':  {'type': 'U', 'opcode': 0b0110111},
    'auipc':{'type': 'U', 'opcode': 0b0010111},
    # J-type
    'jal':  {'type': 'J', 'opcode': 0b1101111},
    # System
    'ecall':{'type': 'SYS', 'opcode': 0b1110011},
    'ebreak':{'type': 'SYS', 'opcode': 0b1110011},
}

def sign_extend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

def parse_mem_operand(operand):
    match = re.match(r'(-?\d+)\((\w+)\)', operand)
    if not match:
        raise ValueError(f"Invalid memory operation format {operand}")
    else:
        imm = int(match.group(1), 0)
        rs1 = match.group(2)
        return imm, rs1

def encode_r_type(opcode, rd, funct3, rs1, rs2, funct7=0):
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def encode_i_type(opcode, rd, funct3, rs1, imm):
    return ((imm & 0xfff) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def encode_s_type(opcode, rs1, rs2, imm, funct3):
    imm11to5 = (imm >> 5) & 0x7f
    imm4to0 = imm & 0x1f
    return (imm11to5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm4to0 << 7) | opcode

def encode_b_type(opcode, rs1, rs2, imm, funct3):
    imm12 = (imm >> 12) & 0x1
    imm10to5 = (imm >> 5) & 0x3f
    imm4to1 = (imm >> 1) & 0xf
    imm11 = (imm >> 11) & 0x1
    return (imm12 << 31) | (imm10to5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm4to1 << 8) | (imm11 << 7) | opcode

def encode_j_type(opcode, rd, imm):
    imm20 = (imm >> 20) & 0x1
    imm10_1 = (imm >> 1) & 0x3ff
    imm11 = (imm >> 11) & 0x1
    imm19_12 = (imm >> 12) & 0xff
    return (imm20 << 31) | (imm19_12 << 12) | (imm11 << 20) | (imm10_1 << 21) | (rd << 7) | opcode


def reg_num(reg):
    if reg in REGISTER_MAP:
        return REGISTER_MAP[reg]
    else:
        raise ValueError(f"Invalid register name: {reg}")
    
def assemble(input_file):
    name, ext = os.path.splitext(input_file)
    if (ext != '.s'):
        raise ValueError("Input file must have .s extension")
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # First pass: collect label addresses
    labels = {}
    pc = 0
    for line in lines:
        line = line.lower().split('#')[0].strip()
        if not line:
            continue
        if line.endswith(":"):
            label = line[:-1]
            labels[label] = pc
        else:
            pc += 4

    with open(f"{name}.bin", "wb") as bin_file:
        # Second pass: assemble instructions
        pc = 0
        for line in lines:
            line = line.split('#')[0].strip()
            if not line or line.endswith(":"):
                continue
            parts = line.replace(",", "").split()
            if parts[0] in INSTRUCTION_SET:
                instr_info = INSTRUCTION_SET[parts[0]]
                opcode = instr_info['opcode']
                if instr_info['type'] == 'R':
                    rd = reg_num(parts[1])
                    rs1 = reg_num(parts[2])
                    rs2 = reg_num(parts[3])
                    funct3 = instr_info['funct3']
                    funct7 = instr_info.get('funct7', 0)
                    instruction = encode_r_type(opcode, rd, funct3, rs1, rs2, funct7)
                elif instr_info['type'] == 'I':
                    rd = reg_num(parts[1])
                    if (parts[0].startswith('l')):
                        imm, rs1 = parse_mem_operand(parts[2])
                        rs1 = reg_num(rs1)
                    else:
                        rs1 = reg_num(parts[2])
                        imm = int(parts[3], 0)
                    imm = sign_extend(imm, 12)
                    if not -2048 <= imm <= 2047:
                        raise ValueError("I-type immediate out of range")
                    funct3 = instr_info['funct3']
                    instruction = encode_i_type(opcode, rd, funct3, rs1, imm)
                elif instr_info['type'] == 'S':
                    rs2 = reg_num(parts[1])
                    imm, rs1_str = parse_mem_operand(parts[2])
                    rs1 = reg_num(rs1_str)
                    if not -2048 <= imm <= 2047:
                        raise ValueError("S-type immediate out of range")
                    funct3 = instr_info['funct3']
                    instruction = encode_s_type(opcode, rs1, rs2, imm, funct3)
                elif instr_info['type'] == 'B':
                    rs1 = reg_num(parts[1])
                    rs2 = reg_num(parts[2])
                    try:
                        imm = int(parts[3])
                    except ValueError:
                        label = parts[3]
                        if label not in labels:
                            raise ValueError(f"Unknown label: {label}")
                        imm = labels[label] - pc
                        if imm % 2 != 0:
                            raise ValueError("Branch target address must be multiple of 2")
                    if not -4096 <= imm <= 4095:
                        raise ValueError("B-type immediate out of range")
                    funct3 = instr_info['funct3']
                    instruction = encode_b_type(opcode, rs1, rs2, imm, funct3)
                elif instr_info['type'] == 'U':
                    rd = reg_num(parts[1])
                    imm = int(parts[2], 0)
                    instruction = ((imm & 0xfffff) << 12) | (rd << 7) | opcode
                elif instr_info['type'] == 'J':
                    rd = reg_num(parts[1])
                    try:
                        imm = int(parts[2], 0)
                        imm = sign_extend(imm, 21)
                    except ValueError:
                        label = parts[2]
                        if label not in labels:
                            raise ValueError(f"Unknown label: {label}")
                        imm = labels[label] - pc
                        if imm % 2 != 0:
                            raise ValueError("Jump target address must be multiple of 2")
                    if not -1048576 <= imm <= 1048575:
                        raise ValueError("J-type immediate out of range")
                    instruction = encode_j_type(opcode, rd, imm)
                elif instr_info['type'] == 'SYS':
                    if parts[0] == 'ecall':
                        instruction = 0x00000073
                    elif parts[0] == 'ebreak':
                        instruction = 0x00100073
                else:
                    raise ValueError(f"Unsupported instruction type: {instr_info['type']}")
                bin_file.write(instruction.to_bytes(4, byteorder='little'))
                pc += 4
            else:
                raise ValueError(f"Unknown instruction: {parts[0]}")