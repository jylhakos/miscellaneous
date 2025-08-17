# Assembly Debugging

## DevOps Setup Commands
```bash
# Complete environment setup
./devops_setup.sh

# Quick assembly build and debug demo
./demo_assembly_debug.sh

# Open VS Code with assembly debugging configuration
code assembly-debug.code-workspace
```

## Assembly Build Commands
```bash
# Build with debug symbols
as --64 --gstabs+ --gdwarf-4 hello.s -o hello.o
ld hello.o -o hello

# Alternative: GCC build (easier debug integration)
gcc -nostdlib -static hello.s -o hello

# Verify debug symbols
objdump -h hello | grep debug
readelf -S hello | grep debug
```

## GDB Assembly Debugging Commands
```bash
# Start debugging
gdb ./hello
(gdb) set disassembly-flavor intel    # Use Intel syntax
(gdb) break _start                    # Set breakpoint at _start
(gdb) run                            # Start program

# Step through assembly
(gdb) stepi                          # Step one instruction
(gdb) nexti                          # Next instruction (skip calls)
(gdb) continue                       # Continue execution

# Register inspection
(gdb) info registers                 # Show all registers
(gdb) info registers rax rbx         # Show specific registers
(gdb) print/x $rax                   # Print register in hex
(gdb) print/t $rflags               # Print flags in binary

# Memory examination
(gdb) x/10i $rip                     # Show next 10 instructions
(gdb) x/s hello_msg                  # Show string at label
(gdb) x/8x $rsp                      # Show 8 hex words from stack
(gdb) disas _start                   # Disassemble function
```

## VS Code Assembly Debugging
```bash
# Install required extensions
code --install-extension ms-vscode.cpptools
code --install-extension 13xforever.language-x86-64-assembly
code --install-extension maziac.asm-code-lens

# Debugging workflow in VS Code:
# 1. Open .s file
# 2. Click line number to set breakpoint
# 3. Press F5 to start debugging
# 4. Use F10 to step through instructions
# 5. Use Debug Console: -exec info registers
```

## Analysis and Testing
```bash
# System call tracing
strace ./hello                       # Trace system calls
strace -c ./hello                   # System call summary

# Binary analysis
objdump -d hello                     # Disassemble binary
readelf -a hello                     # ELF header analysis
nm hello                            # Symbol table
strings hello                       # Extract strings
file hello                          # File type information
size hello                          # Size information

# Performance testing
time ./hello                        # Execution timing
valgrind ./hello                    # Memory analysis

# Hexdump examination
hexdump -C hello | head -10         # First 10 lines of hex dump
```

## VS Code Tasks (Ctrl+Shift+P → Tasks: Run Task)
- **Build Assembly (Debug)**: Assemble with debug symbols
- **Link Assembly**: Link object file to executable
- **Build and Link Assembly**: Complete build process
- **Run Assembly Program**: Execute the program
- **Disassemble Binary**: Show disassembly
- **Analyze with Strace**: System call analysis

## Debug Console Commands (VS Code)
```
-exec info registers                 # Show all registers
-exec x/10i $rip                    # Show next 10 instructions
-exec print $rax                    # Print RAX register
-exec x/s $rsi                      # Show string at RSI
-exec disas _start                  # Disassemble _start function
-exec break *0x401000               # Set breakpoint at address
-exec stepi                         # Step one instruction
-exec continue                      # Continue execution
```

## Common Register Values (x86-64)
```
General Purpose: RAX, RBX, RCX, RDX, RSI, RDI, RBP, RSP
Index Registers: R8, R9, R10, R11, R12, R13, R14, R15
Special: RIP (instruction pointer), RFLAGS (flags)
```

## System Call Numbers (Linux x86-64)
```
sys_write = 1                       # Write to file descriptor
sys_exit = 60                       # Exit program
sys_read = 0                        # Read from file descriptor
sys_open = 2                        # Open file
```

**Quick Start:** Run `./devops_setup.sh` then `./demo_assembly_debug.sh` to see debug in action.

## Troubleshooting
```bash
# Fix GDB permission issues
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope

# Check if debug symbols exist
objdump -h hello | grep debug

# Verify file format
file hello

# Check if program is executable
ls -l hello
```

## File Extensions and Associations
```
.s, .S     Assembly source files
.o         Object files
.elf       Executable files (Linux)
.dis       Disassembly output
.hex       Hexdump output
```

---
