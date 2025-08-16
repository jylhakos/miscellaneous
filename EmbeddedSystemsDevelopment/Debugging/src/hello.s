.section .data
    hello_msg: .ascii "Hello World from Assembly!\n"
    hello_len = . - hello_msg

.section .text
    .global _start

_start:
    # sys_write system call
    mov $1, %rax        # system call number for sys_write
    mov $1, %rdi        # file descriptor 1 (stdout)
    mov $hello_msg, %rsi # message to write
    mov $hello_len, %rdx # message length
    syscall             # call kernel

    # sys_exit system call
    mov $60, %rax       # system call number for sys_exit
    mov $0, %rdi        # exit status
    syscall             # call kernel
