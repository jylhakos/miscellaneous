# Embedded Software Development

This repository provides practical examples and tools for developing embedded software with compilers, programming languages, debugging, inter-process communication (IPC), and real-time operating systems (RTOS).

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Getting Started](#getting-started)
4. [Prerequisites](#prerequisites)
5. [Quick Start](#quick-start)
6. [Contributing](#contributing)
7. [License](#license)

## Overview

This repository contains a structured approach to embedded systems development with the following areas:

- **Compilers**: C/C++ compilation, cross-compilation, and toolchain management
- **Programming**: Multi-language programming examples (Assembly, C, C++, Qt) for RTOS
- **Debugging**: Comprehensive debugging strategies and tools for embedded development
- **IPC**: Inter-Process Communication mechanisms and implementations
- **Operating Systems**: Real-Time Operating Systems concepts and practical examples

## Project Structure

```
EmbeddedSystems/
├── README.md                           # This main project documentation
├── Compilers/                          # Compiler toolchains and cross-compilation
│   ├── README.md                      # Comprehensive compiler guide
│   ├── CMakeLists.txt                 # CMake build configuration
│   ├── Makefile                       # Make build system
│   ├── PROJECT.md                     # Project-specific documentation
│   ├── VALIDATION.md                  # Validation and testing procedures
│   ├── setup-yocto-clang.sh          # Yocto/Clang environment setup
│   ├── scripts/                       # Build and utility scripts
│   │   ├── compare_compilers.sh       # GCC vs Clang comparison
│   │   ├── compiler_check.sh          # Compiler validation
│   │   └── demo.sh                    # Demonstration script
│   ├── src/                           # Source code examples
│   │   ├── ASSEMBLER/                 # Assembly language examples
│   │   │   ├── t_arm.s               # ARM assembly code
│   │   │   └── t.s                   # x86_64 assembly code
│   │   ├── C/                         # C language examples
│   │   │   └── t.c                   # Sample C program with vector operations
│   │   └── C++/                       # C++ language examples
│   │       ├── t.c++                 # C++ program with .c++ extension
│   │       └── t.cpp                 # Sample C++ program
│   ├── toolchains/                    # Cross-compilation toolchain configs
│   │   ├── aarch64-linux-gnu.cmake   # ARM64 toolchain
│   │   └── arm-linux-gnueabihf.cmake # ARM32 toolchain
│   └── yocto-workspace/               # Yocto Linux integration
│       ├── build-demo/               # Yocto build configuration
│       └── meta-compilers-demo/      # Custom Yocto layer
├── Programming/                        # Multi-language programming for RTOS
│   ├── README.md                      # Programming languages guide
│   ├── PROJECT_SUMMARY.md             # Project summary and objectives
│   ├── results/                       # Performance test results
│   ├── scripts/                       # Build and automation scripts
│   │   ├── build_all.sh              # Build all language examples
│   │   ├── demo.sh                   # Demonstration script
│   │   ├── measure_performance.sh    # Performance benchmarking
│   │   ├── README.md                 # Scripts documentation
│   │   └── setup_devenv.sh           # Development environment setup
│   └── src/                           # Source code examples
│       ├── assembler/                 # Assembly language programming
│       │   ├── hello_world.asm       # Assembly hello world
│       │   ├── Makefile              # Assembly build system
│       │   └── README.md             # Assembly documentation
│       ├── c/                         # C language programming
│       │   ├── c_hello_world         # Compiled C binary
│       │   ├── main.c                # C source code
│       │   ├── Makefile              # C build system
│       │   └── README.md             # C documentation
│       ├── cpp/                       # C++ language programming
│       │   ├── cpp_hello_world       # Compiled C++ binary
│       │   ├── main.cpp              # C++ source code
│       │   ├── Makefile              # C++ build system
│       │   └── README.md             # C++ documentation
│       └── qt/                        # Qt framework programming
│           ├── CMakeLists.txt        # Qt CMake configuration
│           ├── main.cpp              # Qt application source
│           └── README.md             # Qt documentation
├── Debugging/                          # Debugging tools and techniques
│   ├── README.md                      # Comprehensive debugging guide
│   ├── ASSEMBLY_DEBUG.md              # Assembly-specific debugging
│   ├── assembly-debug.code-workspace  # VS Code workspace for debugging
│   ├── debug_session.gdb              # GDB session configuration
│   ├── demo_assembly_debug.sh         # Assembly debugging demonstration
│   ├── devops_setup.sh               # DevOps debugging setup
│   └── src/                           # Debug example source code
│       └── hello.s                   # Assembly code for debugging practice
├── IPC/                               # Inter-Process Communication
│   ├── README.md                      # IPC mechanisms and implementations
│   ├── build.sh                       # IPC examples build script
│   └── src/                           # IPC source code examples
│       ├── client/                    # IPC client implementation
│       │   ├── client.pro            # Qt project file for client
│       │   ├── CMakeLists.txt        # CMake configuration
│       │   └── main_client.cpp       # Client source code
│       └── server/                    # IPC server implementation
│           ├── CMakeLists.txt        # CMake configuration
│           ├── main_server.cpp       # Server main source
│           ├── server.cpp            # Server implementation
│           ├── server.h              # Server header file
│           └── server.pro            # Qt project file for server
└── OperatingSystems/                   # Real-Time Operating Systems
    └── README.md                      # RTOS concepts and fundamentals
```

### Folder Descriptions

#### 🔧 Compilers/
**Purpose**: Comprehensive guide to C/C++ compilation, cross-compilation, and toolchain management for embedded systems.

**Features**:
- GCC vs Clang comparison and optimization strategies
- Cross-compilation for ARM architectures (ARM32/ARM64)
- Yocto Linux integration for custom embedded distributions
- Assembly language integration with GNU toolchain
- CMake and Makefile build system examples

**Use Cases**: Setting up development environments, cross-compiling for embedded targets, optimizing code for specific architectures.

#### Programming/
**Purpose**: Multi-language programming examples optimized for Real-Time Operating Systems (RTOS).

**Key Features**:
- Assembly, C, C++, and Qt programming examples
- Performance benchmarking and optimization techniques
- RTOS-specific programming patterns and best practices
- Cross-platform deployment strategies
- Development environment automation scripts

**Use Cases**: Learning embedded programming languages, performance optimization, RTOS application development.

#### Debugging/
**Purpose**: Comprehensive debugging strategies and tools for embedded software development.

**Features**:
- VS Code debugging configuration for C/C++ and Assembly
- GDB command-line debugging techniques
- Assembly language debugging procedures
- Cross-compilation debugging strategies
- DevOps debugging pipeline setup

**Use Cases**: Troubleshooting embedded applications, setting up debugging environments, learning low-level debugging techniques.

#### IPC/
**Purpose**: Inter-Process Communication mechanisms and practical implementations for embedded systems.

**Key Features**:
- Traditional UNIX IPC (pipes, message queues, shared memory)
- POSIX IPC implementations
- Network-based communication (sockets)
- Qt framework IPC integration
- Client-server architecture examples

**Use Cases**: Implementing communication between processes, distributed embedded systems, real-time data sharing.

#### ⚡ OperatingSystems/
**Purpose**: Real-Time Operating Systems (RTOS) concepts, fundamentals, and practical considerations.

**Key Features**:
- Hard vs Soft real-time systems comparison
- RTOS scheduling algorithms and priority management
- Microkernel vs Monolithic system architectures
- Process and thread management in embedded contexts
- Popular RTOS platforms overview (FreeRTOS, VxWorks, QNX, etc.)

**Use Cases**: Understanding RTOS principles, selecting appropriate RTOS platforms, designing real-time embedded applications.

## Getting Started

### Prerequisites

Before executing scripts with this repository, check that you have the following tools installed on your environment.

#### Development Tools
```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade

# Install build essentials
sudo apt-get install build-essential cmake

# Install debugging tools
sudo apt-get install gdb valgrind

# Install version control
sudo apt-get install git
```

#### Cross-Compilation Toolchains
```bash
# Install ARM toolchains
sudo apt-get install gcc-arm-linux-gnueabihf gcc-aarch64-linux-gnu

# Install additional embedded tools
sudo apt-get install binutils-arm-linux-gnueabihf binutils-aarch64-linux-gnu
```

#### Development Environment
```bash
# Install VS Code (if not already installed)
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt-get update
sudo apt-get install code

# Install Qt development framework (optional)
sudo apt-get install qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools
```

## Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd EmbeddedSystems

# Run setup scripts for development environment
./Programming/scripts/setup_devenv.sh
```

### 2. Build All Examples
```bash
# Build all programming language examples
./Programming/scripts/build_all.sh

# Build and test compilers
cd Compilers && make all
```

### 3. Run Demonstrations
```bash
# Programming examples demonstration
./Programming/scripts/demo.sh

# Compiler comparison demonstration
./Compilers/scripts/demo.sh

# Assembly debugging demonstration
./Debugging/demo_assembly_debug.sh
```

### 4. Performance Benchmarking
```bash
# Run performance measurements
./Programming/scripts/measure_performance.sh
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

