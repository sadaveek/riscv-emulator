    addi a0, zero, 0      # sum = 0
    addi a1, zero, 5      # counter = 5
    addi a2, zero, 0      # index = 0

loop:
    add a0, a0, a1        # sum += counter
    addi a1, a1, -1       # counter -= 1
    sw a0, 0(a2)          # store sum to address 0 + a2 (simulate RAM at 0)
    addi a2, a2, 4        # index += 4
    bne a1, zero, loop    # if counter != 0, loop again

    lw a3, 0(zero)        # load first stored sum back to a3 (memory[0])
    ecall