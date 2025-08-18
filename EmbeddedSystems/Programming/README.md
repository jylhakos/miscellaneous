# Embedded Software Development - Programming Languages

## Overview

This project demonstrates programming for Real-Time Operating Systems (RTOS) by Assembly, Qt, C++, and C-languages. The src folder includes examples for Assembly, Qt, C++ and C-languages, performance benchmarking tools, and deployment strategies for embedded systems development.

## Table of Contents

1. [Programming Languages for RTOS](#programming-languages-for-rtos)
   - [Qt for RTOS](#qt-for-rtos)
   - [C++ for RTOS](#c-for-rtos)
   - [C for RTOS](#c-for-rtos)
   - [Assembly x86 for RTOS](#assembly-x86-for-rtos)
2. [Building](#building)
3. [Testing](#testing)
4. [Deployment](#deployment)
5. [Performance and Benchmarking](#performance-and-benchmarking)
6. [Cross-Compilation for RTOS](#cross-compilation-for-rtos)
7. [DevOps Setup](#devops-setup)
8. [Sample Programs](#sample-programs)
9. [References](#references)

## Programming Languages for RTOS

### Qt for RTOS

Qt provides excellent support for embedded systems and RTOS through Qt for MCUs (Microcontroller Units). Qt Quick Ultralite is specifically designed for resource-constrained devices running on bare metal or lightweight RTOS.

**Key Features:**
- Optimized for memory-constrained environments
- Hardware-accelerated graphics
- Real-time performance characteristics
- Static linking capabilities
- Cross-platform deployment

**Performance Considerations:**
- **Framebuffer Strategy**: Choose between single and double buffering based on memory vs. performance trade-offs
- **Font Engine Selection**: Monotype Spark for internationalization, Static engine for lower footprint
- **Caching Strategies**: Image caching, text caching, and font cache priming
- **Hardware Layers**: Utilize hardware acceleration when available

### C++ for RTOS

C++ offers object-oriented programming capabilities while maintaining performance characteristics suitable for RTOS environments.

**Key Features:**
- Object-oriented design patterns
- Template programming for efficiency
- Standard Template Library (STL) subset
- Exception handling (if supported by RTOS)
- Strong type safety

**RTOS Considerations:**
- Avoid dynamic memory allocation in hard real-time contexts
- Use stack-based objects when possible
- Minimize constructor/destructor overhead
- Consider compile-time optimizations

### C for RTOS

C remains the foundation language for RTOS development, offering direct hardware access and predictable performance.

**Key Features:**
- Direct memory management
- Minimal runtime overhead
- Predictable execution times
- Excellent compiler optimization support
- Wide RTOS compatibility

**Best Practices:**
- Use static memory allocation
- Implement deterministic algorithms
- Minimize function call overhead
- Optimize for worst-case execution time (WCET)

### Assembly x86 for RTOS

Assembly language provides the control over hardware resources and execution timing, making it ideal for the most critical RTOS components and time-sensitive operations.

**Key Features:**
- Direct hardware control and register access
- Predictable, cycle-accurate execution timing
- Minimal memory footprint and overhead
- Complete control over system resources
- Optimal performance characteristics

**x86-64 General-Purpose Registers:**
- **RAX/EAX/AX/AL**: Accumulator register for arithmetic operations and function return values
- **RBX/EBX/BX/BL**: Base register, often used as memory base pointer
- **RCX/ECX/CX/CL**: Counter register, frequently used in loop operations
- **RDX/EDX/DX/DL**: Data register for I/O operations and arithmetic overflow
- **RSI/ESI/SI**: Source Index register for string and memory operations
- **RDI/EDI/DI**: Destination Index register for string and memory operations
- **RBP/EBP/BP**: Base Pointer, typically points to the base of the current stack frame
- **RSP/ESP/SP**: Stack Pointer, points to the top of the stack

**Essential x86 Instructions:**
- **MOV**: Move data between registers and memory
- **ADD/SUB**: Arithmetic addition and subtraction
- **MUL/DIV**: Multiplication and division operations
- **PUSH/POP**: Stack operations for data storage
- **CALL/RET**: Subroutine call and return mechanisms
- **JMP/Jcc**: Unconditional and conditional jump instructions
- **SYSCALL/INT**: System call and interrupt invocation

**RTOS Optimization Benefits:**
- Deterministic execution with known cycle counts
- Direct interrupt service routine implementation
- Optimal context switching code
- Hardware abstraction layer implementation
- Critical timing-sensitive code sections

**Hello World Example (x86-64 NASM):**
```assembly
section .data
    msg db "Hello, World!", 0x0A
    len equ $ - msg

section .text
    global _start

_start:
    ; write(1, msg, len)
    mov rax, 1      ; syscall number for 'write'
    mov rdi, 1      ; file descriptor for stdout
    mov rsi, msg    ; address of the message string
    mov rdx, len    ; length of the message
    syscall         ; invoke the system call

    ; exit(0)
    mov rax, 60     ; syscall number for 'exit'
    mov rdi, 0      ; exit code (0 for success)
    syscall         ; invoke the system call
```

## Building

### Qt Applications

#### Prerequisites
```bash
# Install Qt6 development packages
sudo apt-get update
sudo apt-get install qt6-base-dev qt6-tools-dev cmake build-essential
```

#### CMake Configuration
```cmake
cmake_minimum_required(VERSION 3.16)
project(QtHelloWorld VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Core Widgets)
qt_standard_project_setup()

qt_add_executable(QtHelloWorld main.cpp)
target_link_libraries(QtHelloWorld PRIVATE Qt6::Core Qt6::Widgets)
```

#### Build Commands
```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### C++ Applications

#### Build Configuration
```bash
# Compile with optimization and debugging symbols
g++ -O2 -g -Wall -Wextra -std=c++17 -o cpp_hello_world main.cpp

# For RTOS cross-compilation
arm-linux-gnueabihf-g++ -O2 -static -o cpp_hello_world_arm main.cpp
```

### C Applications

#### Build Configuration
```bash
# Standard compilation
gcc -O2 -g -Wall -Wextra -std=c99 -o c_hello_world main.c -lm

# For RTOS cross-compilation
arm-linux-gnueabihf-gcc -O2 -static -o c_hello_world_arm main.c -lm
```

### Assembly Applications

#### Prerequisites
```bash
# Install NASM assembler and development tools
sudo apt-get install nasm build-essential binutils objdump

# For analysis tools
sudo apt-get install strace hexdump readelf
```

#### Build Configuration
```bash
# Standard assembly build
nasm -f elf64 -o hello_world.o hello_world.asm
ld -o hello_world hello_world.o

# Debug build with symbols
nasm -f elf64 -g -F dwarf -o hello_world_debug.o hello_world.asm
ld -o hello_world_debug hello_world_debug.o

# Using Makefile (recommended)
cd src/assembler
make                    # Default build
make debug             # Debug build
make release           # Optimized build
make run               # Build and run
```

## Testing

### Unit Testing Framework Setup

#### For C++ (Google Test)
```bash
# Install Google Test
sudo apt-get install libgtest-dev cmake
cd /usr/src/gtest
sudo cmake CMakeLists.txt
sudo make
sudo cp lib/*.a /usr/lib
```

#### For C (Unity Framework)
```bash
# Clone Unity testing framework
git clone https://github.com/ThrowTheSwitch/Unity.git
```

### Real-Time Testing Techniques

1. **Timing Analysis**
   - Worst-Case Execution Time (WCET) measurement
   - Interrupt latency testing
   - Task switching overhead analysis

2. **Stress Testing**
   - High-frequency interrupt simulation
   - Memory pressure testing
   - CPU utilization stress tests

3. **Endurance Testing**
   - Long-duration runtime testing
   - Memory leak detection
   - Performance degradation monitoring

## Deployment

### Desktop Deployment (Linux/Debian)

#### Qt Application Deployment
```bash
# Create installation directory
mkdir -p deploy/qt_app

# Install application
cmake --install build --prefix deploy/qt_app

# Generate deployment script
qt_generate_deploy_app_script(
    TARGET QtHelloWorld
    OUTPUT_SCRIPT deploy_script
    NO_UNSUPPORTED_PLATFORM_ERROR
)
```

#### Static Binary Deployment
```bash
# Create statically linked binaries
gcc -static -O2 -o c_hello_world_static main.c
g++ -static -O2 -o cpp_hello_world_static main.cpp
```

### RTOS Deployment

#### Cross-Compilation Setup
```bash
# Install cross-compilation toolchain
sudo apt-get install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

# For specific RTOS (e.g., FreeRTOS)
export CC=arm-none-eabi-gcc
export CXX=arm-none-eabi-g++
```

#### Deployment Strategies
1. **Flash Programming**: Direct firmware upload to target hardware
2. **Network Deployment**: Over-the-air updates via Ethernet/WiFi
3. **SD Card Deployment**: Bootable image creation
4. **JTAG Programming**: Debug interface deployment

## Performance and Benchmarking

### Key Metrics for RTOS

1. **Latency & Jitter**
   - Interrupt response time
   - Task scheduling latency
   - System call overhead

2. **Throughput**
   - Data processing rate
   - Task completion rate
   - I/O bandwidth utilization

3. **Resource Utilization**
   - CPU utilization percentage
   - Memory footprint (RAM/ROM)
   - Stack usage per task

### Measurement Tools

#### Linux Performance Tools
```bash
# Install performance monitoring tools
sudo apt-get install linux-perf-tools trace-cmd kernelshark valgrind

# CPU performance monitoring
perf stat ./program

# Memory profiling
valgrind --tool=massif ./program

# System-wide monitoring
htop
vmstat 1
iostat 1
```

#### RTOS-Specific Tools
- **Tracealyzer**: RTOS kernel tracing and visualization
- **SEGGER SystemView**: Real-time recording and visualization
- **IAR I-jet Trace**: Hardware-assisted tracing

### Benchmarking Framework

#### Micro-benchmarking
```cpp
// Example timing measurement
#include <chrono>

auto start = std::chrono::high_resolution_clock::now();
// Code to benchmark
auto end = std::chrono::high_resolution_clock::now();
auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
```

#### Language Performance Comparison

| Metric | Assembly | C | C++ | Qt |
|--------|----------|---|-----|-----|
| Binary Size | Smallest | Small | Medium | Largest |
| Memory Usage | Minimal | Minimal | Low | Higher |
| Startup Time | Fastest | Fastest | Fast | Slower |
| Development Speed | Slowest | Slower | Medium | Fastest |
| RTOS Compatibility | Perfect | Excellent | Good | Limited |
| Execution Speed | Fastest | Fastest | Fast | Good |
| Hardware Control | Complete | Direct | Indirect | Abstract |

## Cross-Compilation for RTOS

### Toolchain Setup

#### ARM Cortex-M (FreeRTOS)
```bash
# Install ARM GCC toolchain
sudo apt-get install gcc-arm-none-eabi

# Set environment variables
export PATH=$PATH:/usr/bin/arm-none-eabi-gcc
export CROSS_COMPILE=arm-none-eabi-
```

#### ARM Linux (Embedded Linux)
```bash
# Install cross-compilation tools
sudo apt-get install gcc-arm-linux-gnueabihf

# Configure for specific target
export CC=arm-linux-gnueabihf-gcc
export CXX=arm-linux-gnueabihf-g++
export AR=arm-linux-gnueabihf-ar
export STRIP=arm-linux-gnueabihf-strip
```

### Qt Cross-Compilation

#### Device Configuration
```bash
# Configure Qt for embedded target
./configure -device linux-rasp-pi4-v3d-g++ \
           -device-option CROSS_COMPILE=arm-linux-gnueabihf- \
           -sysroot /path/to/sysroot \
           -prefix /opt/qt6-pi
```

## DevOps Setup

### Continuous Integration Tools

#### Build Automation (Jenkins)
```bash
# Install Jenkins
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install jenkins
```

#### Version Control Integration
```bash
# Git hooks for automated building
#!/bin/bash
# pre-commit hook
make clean
make all
make test
```

### Automated Testing Pipeline

#### Static Analysis
```bash
# Install static analysis tools
sudo apt-get install cppcheck clang-tidy

# Run static analysis
cppcheck --enable=all --std=c++17 src/
clang-tidy src/*.cpp -- -std=c++17
```

#### Dynamic Analysis
```bash
# Runtime analysis with Valgrind
valgrind --leak-check=full --track-origins=yes ./program

# Address Sanitizer
gcc -fsanitize=address -g -o program_asan program.c
```

### Assembly Development Tools

#### NASM Assembler Setup
```bash
# Install NASM and associated tools
sudo apt-get install nasm build-essential

# For cross-development
sudo apt-get install binutils-dev objdump hexdump

# Verify installation
nasm -version
ld --version
```

#### Assembly Analysis Tools
```bash
# Disassembly and analysis
objdump -d program          # Disassemble executable
readelf -a program          # ELF file analysis
hexdump -C program          # Hex dump
nm program                  # Symbol table

# Performance analysis
perf stat ./program         # Hardware performance counters
strace ./program            # System call tracing
```

#### Assembly Debugging
```bash
# Build with debug symbols
nasm -f elf64 -g -F dwarf -o program.o program.asm
ld -o program program.o

# Debug with GDB
gdb program
(gdb) layout asm           # Show assembly view
(gdb) stepi                # Step instruction by instruction
(gdb) info registers       # Show register values
```

## Sample Programs for Assembly, Qt, C++ and C-languages

The following sample programs are available in the `src/` directory:

- `src/qt/`: Qt-based "Hello World" application
- `src/cpp/`: C++ "Hello World" application
- `src/c/`: C "Hello World" application
- `src/assembler/`: Assembly x86-64 "Hello World" application
- `scripts/`: Performance measurement scripts

### Compilation Instructions

See individual README files in each language directory for specific compilation and execution instructions.

## References

### Qt Documentation
- [Qt CMake Manual](https://doc.qt.io/qt-6/cmake-manual.html) - Official Qt CMake build system documentation
- [Qt Deployment Guide](https://doc.qt.io/qt-6/cmake-deployment.html) - Cross-platform deployment strategies
- [Qt for MCUs Performance Guide](https://doc.qt.io/QtForMCUs/performance-guide-application-performance.html) - Optimization techniques for embedded systems

### RTOS Performance Analysis
- [FreeRTOS Performance Analysis](https://mcuoneclipse.com/2018/02/25/performance-and-runtime-analysis-with-freertos/)

### Development Tools
- [CMake Documentation](https://cmake.org/cmake/help/latest/) - Build system configuration
- [GCC Manual](https://gcc.gnu.org/onlinedocs/gcc/) - Compiler optimization guide
- [Valgrind User Manual](https://valgrind.org/docs/manual/manual.html) - Memory debugging and profiling

### Standards and Best Practices
- [MISRA C Guidelines](https://www.misra.org.uk/) - Safety-critical C programming standards
- [Real-Time Systems Design Principles](https://www.embedded.com/) - Embedded systems development resources

### Assembly Language
- [x86 Assembly Guide - University of Virginia](https://www.cs.virginia.edu/~evans/cs216/guides/x86.html) -  x86 assembly programming
- [Intel 64 and IA-32 Software Developer's Manual](https://software.intel.com/content/www/us/en/develop/articles/intel-sdm.html) - Official processor documentation
- [NASM Documentation](https://nasm.us/docs.php) - NASM assembler reference
- [Linux System Call Reference](https://filippo.io/linux-syscall-table/) - System call interface documentation
