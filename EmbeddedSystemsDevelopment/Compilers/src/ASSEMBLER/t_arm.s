@ t_arm.s - ARM32 Assembly equivalent of C program
@ Demonstrates ARM assembly language and system calls
@ Equivalent to: printf("Hello ARM World!\n");

.section .data
    hello_msg:
        .ascii "===== ARM Assembly Demonstration =====\n"
        .ascii "Architecture: ARM32 (ARMv7)\n"
        .ascii "Assembler: GNU AS for ARM\n" 
        .ascii "Hello ARM World!\n"
        .ascii "===== End of ARM Assembly Demo =====\n"
    
    hello_len = . - hello_msg    @ Calculate string length

.section .text
    .global _start

_start:
    @ Write system call - ARM Linux ABI
    @ write(fd, buffer, count)
    mov r0, #1              @ file descriptor (stdout = 1)
    ldr r1, =hello_msg      @ address of message
    ldr r2, =hello_len      @ number of bytes to write
    mov r7, #4              @ system call number for write (4)
    svc #0                  @ software interrupt (system call)

    @ Exit system call
    @ exit(status)
    mov r0, #0              @ exit status (0 = success)
    mov r7, #1              @ system call number for exit (1)  
    svc #0                  @ software interrupt (system call)

@ Alternative version using libc printf (requires linking with libc)
@ Compile with: arm-linux-gnueabihf-gcc -o hello_arm t_arm.s
@
@ .section .data
@     format_str: .asciz "===== ARM with libc =====\nHello ARM World!\n"
@ 
@ .section .text
@     .global main
@ 
@ main:
@     @ Save link register
@     push {lr}
@     
@     @ Call printf
@     ldr r0, =format_str     @ First argument (format string)
@     bl printf               @ Branch with link to printf
@     
@     @ Return 0
@     mov r0, #0
@     
@     @ Restore link register and return
@     pop {pc}

@ ARM Assembly Features Demonstrated:
@ - ARM instruction set (32-bit)
@ - System call interface (Linux ARM EABI)
@ - Memory addressing with labels
@ - Immediate values with # prefix
@ - Register usage (r0-r7 for arguments and scratch)
@ - Software interrupt (svc) for system calls
@ - ARM calling convention compatibility
