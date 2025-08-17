; Hello World program in x86-64 Assembly using NASM syntax
; This program demonstrates basic RTOS-compatible assembly programming
; Author: Embedded Systems Development Project
; Target: Linux x86-64

section .data
    ; Define string constants
    msg db 'Hello World!', 0x0A    ; Message with newline
    msg_len equ $ - msg                          ; Calculate message length
    
    ; Performance test message
    perf_msg db 'Assembly Performance Test Complete!', 0x0A
    perf_msg_len equ $ - perf_msg
    
    ; Application info
    info_msg db 'x86-64 Assembly - RTOS Optimized', 0x0A
    info_len equ $ - info_msg
    
    ; Newline character
    newline db 0x0A
    newline_len equ $ - newline

section .bss
    ; Reserve space for performance test variables
    result resq 1        ; Reserve 8 bytes for 64-bit result
    counter resq 1       ; Reserve 8 bytes for counter

section .text
    global _start

; Performance test routine
performance_test:
    ; Save registers
    push rax
    push rbx
    push rcx
    push rdx
    
    ; Initialize counter and result
    mov rcx, 1000000     ; Set loop counter to 1 million
    xor rax, rax         ; Clear accumulator
    
.loop:
    ; Simple arithmetic operations
    add rax, rcx         ; Add counter to accumulator
    imul rax, 2          ; Multiply by 2
    shr rax, 1           ; Divide by 2 (shift right)
    dec rcx              ; Decrement counter
    jnz .loop            ; Jump if not zero
    
    ; Store result
    mov [result], rax
    
    ; Restore registers
    pop rdx
    pop rcx  
    pop rbx
    pop rax
    ret

; Print string routine
; Input: RSI = string address, RDX = string length
print_string:
    push rax
    push rdi
    
    ; System call: write(stdout, string, length)
    mov rax, 1           ; syscall number for sys_write
    mov rdi, 1           ; file descriptor (stdout)
    ; rsi already contains string address
    ; rdx already contains string length
    syscall              ; invoke system call
    
    pop rdi
    pop rax
    ret

; Print application information
print_info:
    push rsi
    push rdx
    
    ; Print application info
    mov rsi, info_msg
    mov rdx, info_len
    call print_string
    
    pop rdx
    pop rsi
    ret

; Main program entry point
_start:
    ; Print application information
    call print_info
    
    ; Print Hello World message
    mov rsi, msg         ; Load address of message
    mov rdx, msg_len     ; Load message length
    call print_string
    
    ; Run performance test
    call performance_test
    
    ; Print performance test completion message
    mov rsi, perf_msg
    mov rdx, perf_msg_len
    call print_string
    
    ; Print newline for formatting
    mov rsi, newline
    mov rdx, newline_len
    call print_string
    
    ; Exit program
    mov rax, 60          ; syscall number for sys_exit
    mov rdi, 0           ; exit status (0 = success)
    syscall              ; invoke system call

; Program metadata (for debugging and information)
section .comment
    db "Assembly Hello World - RTOS Compatible"
    db "Built with NASM for x86-64 Linux"
    db "Optimized for embedded systems development"
