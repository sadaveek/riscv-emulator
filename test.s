.section .text
.globl _start

_start:
    # Initialize x1 = 5 (small immediate)
    addi x1, x0, 5        # x1 = 5
    addi x1, x1, 3        # x1 = 8
    addi x1, x1, 7        # x1 = 15

    # Initialize x2 = 10 (small immediate)
    addi x2, x0, 10       # x2 = 10

    # Initialize x3 = -1 by subtracting 1 from zero repeatedly
    addi x3, x0, 0        # x3 = 0
    addi x3, x3, -1       # x3 = -1 (0xFFFFFFFF)

    # Initialize x4 = 1 (small immediate)
    addi x4, x0, 1        # x4 = 1

    # Now R-type operations

    add x5, x1, x2        # x5 = x1 + x2 = 15 + 10 = 25
    sub x6, x1, x2        # x6 = x1 - x2 = 15 - 10 = 5
    xor x7, x2, x4        # x7 = 10 ^ 1 = 11 (0xB)
    or  x8, x2, x4        # x8 = 10 | 1 = 11 (0xB)
    and x9, x2, x4        # x9 = 10 & 1 = 0
    sll x10, x4, x2       # x10 = 1 << 10 = 1024 (0x400)
    srl x11, x3, x4       # x11 = 0xFFFFFFFF >> 1 = 0x7FFFFFFF
    sra x12, x3, x4       # x12 = arithmetic right shift of -1 by 1 = 0xFFFFFFFF
    slt x13, x6, x2       # x13 = (5 < 10) = 1 (signed)
    sltu x14, x3, x2      # x14 = (0xFFFFFFFF < 10) unsigned? 0

    ecall                 # end program
