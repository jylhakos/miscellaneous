# Assembly x86-64 Hello World

## Overview
This Assembly language implementation demonstrates low-level system programming for RTOS environments using x86-64 architecture. The program showcases direct system calls, register manipulation, and memory management without any high-level language abstractions.

## Features
- x86-64 assembly implementation using NASM syntax
- Linux system calls (sys_write, sys_exit)
- Performance benchmarking loop
- RTOS-optimized register usage
- Minimal memory footprint
- No external library dependencies

## x86-64 Architecture

### General-Purpose Registers
The x86-64 architecture provides 16 general-purpose registers, each 64-bit wide:

#### Primary Registers (64-bit/32-bit/16-bit/8-bit)
- **RAX/EAX/AX/AL**: Accumulator register - arithmetic operations, function return values
- **RBX/EBX/BX/BL**: Base register - memory base pointer, general storage
- **RCX/ECX/CX/CL**: Counter register - loop counter, shift operations
- **RDX/EDX/DX/DL**: Data register - I/O operations, arithmetic overflow
- **RSI/ESI/SI/SIL**: Source Index - string operations source pointer
- **RDI/EDI/DI/DIL**: Destination Index - string operations destination pointer  
- **RBP/EBP/BP/BPL**: Base Pointer - stack frame base reference
- **RSP/ESP/SP/SPL**: Stack Pointer - current stack top

#### Extended Registers (64-bit only)
- **R8-R15**: Additional general-purpose registers (R8D, R8W, R8B for 32/16/8-bit)

### Key Instructions Used

#### Data Movement
- `mov reg, value` - Move immediate value to register
- `mov reg, [addr]` - Load from memory address
- `mov [addr], reg` - Store to memory address

#### Arithmetic Operations
- `add reg, value` - Addition
- `sub reg, value` - Subtraction
- `imul reg, value` - Signed multiplication
- `shr reg, count` - Shift right (division by powers of 2)
- `inc reg` / `dec reg` - Increment/decrement

#### Control Flow
- `jmp label` - Unconditional jump
- `jnz label` - Jump if not zero
- `call label` - Call subroutine
- `ret` - Return from subroutine

#### System Interface
- `syscall` - Invoke system call (Linux x86-64)

## Prerequisites

### Required Tools
```bash
# Install NASM assembler and development tools
sudo apt-get update
sudo apt-get install nasm build-essential binutils

# For analysis tools (optional)
sudo apt-get install strace hexdump objdump readelf
```

### Verify Installation
```bash
# Check NASM version
nasm -version

# Check linker
ld --version
```

## Building

### Quick Build
```bash
# Default build
make

# Run the program
make run
```

### Build Variations
```bash
# Debug build with symbols
make debug

# Optimized release build
make release

# Static linking
make static

# 32-bit build (if needed)
make build32
```

### Manual Build Process
```bash
# Assemble source to object file
nasm -f elf64 -o hello_world.o hello_world.asm

# Link object file to executable
ld -o hello_world hello_world.o

# Run the program
./hello_world
```

## Usage

### Basic Execution
```bash
# Run the program
./hello_world

# Output:
# x86-64 Assembly - RTOS Optimized
# Hello World from Assembly!
# Assembly Performance Test Complete!
```

### Performance Testing
```bash
# Run with timing
make time-run

# Performance analysis
make perf-test
```

### Analysis Tools
```bash
# Display binary information
make info

# Create disassembly
make disassemble

# Generate hex dump
make hexdump

# Source code analysis
make analyze
```

## Performance

### Binary Size
- Executable size: ~1-2 KB (extremely compact)
- No external dependencies
- Pure machine code

### Memory Usage
- Minimal RAM footprint (~4-8 KB)
- Direct memory addressing
- No heap allocation
- Stack usage: <1 KB

### Execution Speed
- Direct system calls (no library overhead)
- Optimized register usage
- Predictable execution time
- Typical execution: <1 millisecond

## RTOS Optimization Features

### Memory Management
- Static memory allocation only
- Predictable memory usage
- No dynamic allocation
- Efficient register utilization

### Real-Time Characteristics
- Deterministic execution paths
- Minimal instruction count
- Direct hardware interface
- No garbage collection overhead

### System Integration
- Direct system call interface
- Minimal kernel interaction
- Predictable timing behavior
- Low interrupt latency impact

## Assembly Language Concepts

### System Calls (Linux x86-64)
```assembly
; sys_write(fd, buffer, count)
mov rax, 1          ; syscall number
mov rdi, 1          ; file descriptor (stdout)
mov rsi, msg        ; buffer address
mov rdx, msg_len    ; byte count
syscall             ; invoke kernel

; sys_exit(status)
mov rax, 60         ; syscall number
mov rdi, 0          ; exit status
syscall             ; invoke kernel
```

### Memory Sections
- `.data` - Initialized data (read-write)
- `.bss` - Uninitialized data (zero-initialized)
- `.text` - Executable code (read-only)
- `.comment` - Metadata (not loaded)

### Addressing Modes
```assembly
mov rax, 42         ; Immediate addressing
mov rax, [rbx]      ; Direct memory addressing
mov rax, [rbx+8]    ; Base + displacement
mov rax, [rbx+rcx*2]; Base + index*scale
```

## Cross-Platform Considerations

### Linux x86-64 (Current Implementation)
- NASM syntax
- System V ABI calling convention
- Linux system calls

### Adaptations
```bash
# Windows x86-64 (MASM syntax)
# - Different assembler syntax
# - Windows API calls
# - Different ABI

# Embedded ARM (if cross-compiling)
# - Different instruction set
# - ARM calling convention
# - Bare-metal system calls
```

## Development Workflow

### Edit-Build-Test Cycle
```bash
# 1. Edit source code
vim hello_world.asm

# 2. Build and test
make clean && make && make run

# 3. Analyze results
make info
make disassemble
```

### Debugging
```bash
# Build with debug symbols
make debug

# Debug with GDB
gdb hello_world_debug

# Trace system calls
strace ./hello_world
```

## Advanced Features

### Performance Optimization
- Hand-optimized assembly code
- Efficient register allocation
- Minimized memory access
- Optimized instruction selection

### Code Analysis
```bash
# Instruction count
objdump -d hello_world | wc -l

# Binary analysis
readelf -a hello_world

# Performance profiling
perf stat ./hello_world
```

## Integration with Other Languages

### Calling from C/C++
```c
// External assembly function
extern void assembly_function(void);

int main() {
    assembly_function();
    return 0;
}
```

### Assembly in C (Inline)
```c
int main() {
    __asm__ volatile (
        "mov $1, %%rax\n\t"
        "mov $1, %%rdi\n\t"
        "mov $msg, %%rsi\n\t"
        "mov $13, %%rdx\n\t"
        "syscall"
        :
        :
        : "rax", "rdi", "rsi", "rdx"
    );
    return 0;
}
```

## Troubleshooting

### Build Issues
```bash
# NASM not found
sudo apt-get install nasm

# Linking errors
sudo apt-get install binutils

# 32-bit compatibility (if needed)
sudo apt-get install gcc-multilib
```

### Runtime Issues
```bash
# Check executable format
file hello_world

# Verify permissions
chmod +x hello_world

# Check library dependencies (should be none)
ldd hello_world
```

### Performance Issues
```bash
# CPU frequency scaling
sudo cpufreq-set -g performance

# Process priority
sudo nice -n -20 ./hello_world

# Memory layout
cat /proc/[pid]/maps
```

## References

### x86-64 Architecture
- [Intel 64 and IA-32 Software Developer's Manual](https://software.intel.com/content/www/us/en/develop/articles/intel-sdm.html)
- [x86 Assembly Guide - University of Virginia](https://www.cs.virginia.edu/~evans/cs216/guides/x86.html)
- [AMD64 ABI Reference](https://github.com/hjl-tools/x86-psABI/wiki/X86-psABI)

### Assembly Programming
- [NASM Documentation](https://nasm.us/docs.php)
- [Linux System Call Reference](https://filippo.io/linux-syscall-table/)
- [Assembly Language Programming Tutorial](https://asmtutor.com/)

### RTOS Development
- [Real-Time Systems Programming](https://www.embedded.com/)
- [Assembly for Embedded Systems](https://embeddedartistry.com/)
