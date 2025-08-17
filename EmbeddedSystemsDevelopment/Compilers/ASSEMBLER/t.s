# t.s - x86_64 Assembly equivalent of C program
# Demonstrates basic system calls and string output
# Equivalent to: printf("Hello World from Assembly!\n");

.section .data
    # String constants
    hello_msg:
        .ascii "===== Assembly Language Demonstration =====\n"
        .ascii "Architecture: x86_64 Linux\n"
        .ascii "Assembler: GNU AS (Gas)\n"
        .ascii "Hello World from Assembly!\n"
        .ascii "===== End of Assembly Demo =====\n\0"
    
    hello_len = . - hello_msg - 1    # Calculate string length (excluding null terminator)

.section .text
    .global _start

_start:
    # Write system call
    # write(stdout, message, length)
    mov $1, %rax        # sys_write system call number (1)
    mov $1, %rdi        # file descriptor (stdout = 1)
    mov $hello_msg, %rsi # message to write
    mov $hello_len, %rdx # number of bytes to write
    syscall             # invoke system call

    # Exit system call
    # exit(status)
    mov $60, %rax       # sys_exit system call number (60)
    mov $0, %rdi        # exit status (0 = success)
    syscall             # invoke system call

# Alternative version using libc printf (requires linking with libc)
# Uncomment and use with: gcc -o hello t.s
#
# .section .data
#     format_str: .string "===== Assembly with libc =====\nHello World from Assembly!\n"
# 
# .section .text
#     .global main
# 
# main:
#     # Save base pointer
#     push %rbp
#     mov %rsp, %rbp
#     
#     # Call printf
#     mov $format_str, %rdi   # First argument (format string)
#     mov $0, %rax           # Number of vector registers used (0)
#     call printf
#     
#     # Return 0
#     mov $0, %rax
#     
#     # Restore base pointer and return
#     pop %rbp
#     ret
