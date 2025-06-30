    .section .text
    .globl _start

_start:
    # ----- LUI & AUIPC -----
    lui x1, 0x12345         # x1 = 0x12345000
    auipc x2, 0x1           # x2 = PC + 0x1000

    # ----- Immediate Arithmetic -----
    addi x3, x1, 10         # x3 = x1 + 10
    xori x4, x3, 0xff       # x4 = x3 ^ 0xff
    ori x5, x4, 0x7f0       # x5 = x4 | 0x7f0
    andi x6, x5, 0x0f0      # x6 = x5 & x0f0
    slli x7, x6, 2          # x7 = x6 << 2
    srli x8, x7, 1          # x8 = x7 >> 1 (logical)
    srai x9, x8, 1          # x9 = x8 >> 1 (arith)
    slti x10, x9, 1000      # x10 = x9 if x9 < 1000
    sltiu x11, x9, 2047     # x11 = x9 if x9 (unsigned) < 2047

    # ----- R-type Operations -----
    add x12, x1, x3         # x12 = x1 + x3
    sub x13, x12, x3        # x13 = x12 - x3
    xor x14, x13, x1        # x14 = x13 ^ x1
    or  x15, x14, x4        # x15 = x14 | x4
    and x16, x15, x5        # x16 = x15 & x5
    sll x17, x16, x6        # x17 = x16 << (x6 & 0x1f)
    srl x18, x17, x6        # x18 = x17 >> (x6 & 0x1f)
    sra x19, x18, x6        # x19 = x18 >> (arith)
    slt x20, x1, x3         # x20 = (x1 < x3) ? 1 : 0
    sltu x21, x1, x2        # x21 = (x1 < x2 unsigned) ? 1 : 0

    # ----- Store/Load -----
    addi x22, x0, 100       # x22 = 100
    sw x22, 0(x0)           # store word at address 0
    lw x23, 0(x0)           # x23 = memory[0]

    addi x22, x0, -1        # x22 = 0xffffffff
    sb x22, 4(x0)           # store byte
    lb x24, 4(x0)           # x24 = sign-extended byte
    lbu x25, 4(x0)          # x25 = zero-extended byte

    sh x22, 8(x0)           # store halfword
    lh x26, 8(x0)           # sign-extended
    lhu x27, 8(x0)          # zero-extended

    # ----- Branches -----
    beq x1, x1, label_eq    # should branch
    addi x28, x0, 0         # skipped if branch works

label_eq:
    bne x1, x0, label_ne    # should branch
    addi x29, x0, 0         # skipped

label_ne:
    blt x0, x1, label_lt    # should branch
    addi x30, x0, 0         # skipped

label_lt:
    bge x1, x0, label_ge    # should branch
    addi x31, x0, 0         # skipped

label_ge:
    bltu x0, x1, label_ltu  # unsigned branch
    nop

label_ltu:
    bgeu x1, x0, label_bgeu
    nop

label_bgeu:

    # ----- Jumps -----
    jal x5, jump_target     # x5 = return addr, jump
    addi x6, x0, 999        # skipped

jump_target:
    jalr x7, 0(x5)          # jump back to x5 (return addr)

    # ----- ECALL/EBREAK -----
    li x10, 0
    ecall                  # should exit

    # unreachable
    li x10, 1
    ebreak
