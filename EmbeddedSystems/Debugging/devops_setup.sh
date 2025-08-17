#!/bin/bash
# DevOps Assembly Debugging Setup Script
# This script sets up a complete assembly debugging environment for development teams

set -e

echo "=== Assembly Debugging Environment Setup ==="
echo "Setting up comprehensive assembly debugging tools..."

# Update system
echo "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# Install essential assembly development tools
echo "Installing assembly development tools..."
sudo apt-get install -y \
    binutils \
    gdb \
    gdb-multiarch \
    nasm \
    yasm \
    build-essential \
    libc6-dev \
    strace \
    ltrace \
    hexdump \
    objdump \
    readelf \
    nm \
    strings \
    valgrind \
    qemu-user \
    qemu-system-x86 \
    lldb

# Install VS Code if not present
if ! command -v code &> /dev/null; then
    echo "Installing VS Code..."
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
    sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
    sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
    sudo apt-get update
    sudo apt-get install -y code
fi

# Install VS Code extensions for assembly debugging
echo "Installing VS Code extensions..."
code --install-extension ms-vscode.cpptools
code --install-extension 13xforever.language-x86-64-assembly
code --install-extension maziac.asm-code-lens
code --install-extension webfreak.debug

# Configure debugging permissions
echo "Configuring debugging permissions..."
echo 'kernel.yama.ptrace_scope = 0' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Create workspace structure
echo "Creating assembly debugging workspace..."
mkdir -p ~/assembly-workspace/{src,build,tools,scripts,logs}
cd ~/assembly-workspace

# Create build script for assembly
cat > scripts/build_assembly.sh << 'EOF'
#!/bin/bash
# Assembly build script with comprehensive debug support

ASM_FILE="$1"
if [ -z "$ASM_FILE" ]; then
    echo "Usage: $0 <assembly_file.s>"
    exit 1
fi

OUTPUT_NAME="${ASM_FILE%.*}"
BUILD_DIR="../build"

echo "Building $ASM_FILE with debug symbols..."
mkdir -p "$BUILD_DIR"

# Assemble with debug info
as --64 --gstabs+ --gdwarf-4 "$ASM_FILE" -o "$BUILD_DIR/${OUTPUT_NAME}.o"

# Link with debug info  
ld "$BUILD_DIR/${OUTPUT_NAME}.o" -o "$BUILD_DIR/$OUTPUT_NAME"

# Generate debug information files
objdump -d "$BUILD_DIR/$OUTPUT_NAME" > "$BUILD_DIR/${OUTPUT_NAME}.dis"
objdump -s "$BUILD_DIR/$OUTPUT_NAME" > "$BUILD_DIR/${OUTPUT_NAME}.hex"
readelf -a "$BUILD_DIR/$OUTPUT_NAME" > "$BUILD_DIR/${OUTPUT_NAME}.elf"
nm "$BUILD_DIR/$OUTPUT_NAME" > "$BUILD_DIR/${OUTPUT_NAME}.symbols"

echo "Build complete:"
echo "  Executable: $BUILD_DIR/$OUTPUT_NAME"
echo "  Object:     $BUILD_DIR/${OUTPUT_NAME}.o"
echo "  Disasm:     $BUILD_DIR/${OUTPUT_NAME}.dis"
echo "  ELF Info:   $BUILD_DIR/${OUTPUT_NAME}.elf"
EOF

chmod +x scripts/build_assembly.sh

# Create automated debugging script
cat > scripts/debug_assembly.sh << 'EOF'
#!/bin/bash
# Automated assembly debugging script

PROGRAM="$1"
if [ -z "$PROGRAM" ]; then
    echo "Usage: $0 <program_path>"
    exit 1
fi

LOGDIR="../logs"
mkdir -p "$LOGDIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOGFILE="$LOGDIR/debug_session_${TIMESTAMP}.log"

echo "=== Assembly Debug Session ===" | tee "$LOGFILE"
echo "Program: $PROGRAM" | tee -a "$LOGFILE"
echo "Timestamp: $(date)" | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"

# File information
echo "=== Binary Information ===" | tee -a "$LOGFILE"
file "$PROGRAM" | tee -a "$LOGFILE"
size "$PROGRAM" | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"

# System call trace
echo "=== System Call Analysis ===" | tee -a "$LOGFILE"
strace -c "$PROGRAM" 2>&1 | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"

# GDB automated debugging
echo "=== GDB Analysis ===" | tee -a "$LOGFILE"
cat > /tmp/gdb_commands << 'GDBEOF'
set disassembly-flavor intel
set logging file debug.gdb.log
set logging on
file PROGRAM_PLACEHOLDER
info file
disas _start
info registers
quit
GDBEOF

sed "s/PROGRAM_PLACEHOLDER/$PROGRAM/" /tmp/gdb_commands | gdb -batch -x - 2>&1 | tee -a "$LOGFILE"
rm -f /tmp/gdb_commands

echo "Debug session complete. Log saved to: $LOGFILE"
EOF

chmod +x scripts/debug_assembly.sh

# Create testing script
cat > scripts/test_assembly.sh << 'EOF'
#!/bin/bash
# Assembly program testing framework

TEST_DIR="../src"
BUILD_DIR="../build"
LOGS_DIR="../logs"

if [ ! -d "$TEST_DIR" ]; then
    echo "Test directory $TEST_DIR not found"
    exit 1
fi

mkdir -p "$LOGS_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEST_LOG="$LOGS_DIR/test_results_${TIMESTAMP}.log"

echo "=== Assembly Testing Framework ===" | tee "$TEST_LOG"
echo "Starting automated tests..." | tee -a "$TEST_LOG"

PASSED=0
FAILED=0

for ASM_FILE in "$TEST_DIR"/*.s; do
    if [ -f "$ASM_FILE" ]; then
        echo "Testing $(basename "$ASM_FILE")..." | tee -a "$TEST_LOG"
        
        # Build the program
        if ./build_assembly.sh "$ASM_FILE" 2>&1 | tee -a "$TEST_LOG"; then
            PROGRAM_NAME=$(basename "$ASM_FILE" .s)
            PROGRAM_PATH="$BUILD_DIR/$PROGRAM_NAME"
            
            # Test execution
            if [ -x "$PROGRAM_PATH" ]; then
                echo "  Executing $PROGRAM_NAME..." | tee -a "$TEST_LOG"
                if timeout 5s "$PROGRAM_PATH" > /tmp/test_output 2>&1; then
                    echo "  ✓ Execution successful" | tee -a "$TEST_LOG"
                    cat /tmp/test_output | tee -a "$TEST_LOG"
                    ((PASSED++))
                else
                    echo "  ✗ Execution failed" | tee -a "$TEST_LOG"
                    ((FAILED++))
                fi
            else
                echo "  ✗ Build failed - no executable created" | tee -a "$TEST_LOG"
                ((FAILED++))
            fi
        else
            echo "  ✗ Build failed" | tee -a "$TEST_LOG"
            ((FAILED++))
        fi
        echo "" | tee -a "$TEST_LOG"
    fi
done

echo "=== Test Results ===" | tee -a "$TEST_LOG"
echo "Passed: $PASSED" | tee -a "$TEST_LOG"
echo "Failed: $FAILED" | tee -a "$TEST_LOG"
echo "Test log: $TEST_LOG"

if [ $FAILED -eq 0 ]; then
    echo "All tests passed! ✓"
    exit 0
else
    echo "Some tests failed! ✗"
    exit 1
fi
EOF

chmod +x scripts/test_assembly.sh

# Create GDB configuration
cat > tools/gdbinit_assembly << 'EOF'
# GDB configuration for assembly debugging
set disassembly-flavor intel
set confirm off
set output-radix 16
set print pretty on

# Custom layout for assembly debugging
define asm-layout
    layout asm
    layout regs
    focus cmd
end

# Step instruction and show next
define hookpost-stepi
    x/i $rip
end

# Show all general purpose registers
define regs64
    info registers rax rbx rcx rdx rsi rdi rbp rsp r8 r9 r10 r11 r12 r13 r14 r15
end

# Show flags register details
define flags
    printf "CF=%d PF=%d AF=%d ZF=%d SF=%d TF=%d IF=%d DF=%d OF=%d\n", \
           ($eflags>>0)&1, ($eflags>>2)&1, ($eflags>>4)&1, ($eflags>>6)&1, \
           ($eflags>>7)&1, ($eflags>>8)&1, ($eflags>>9)&1, ($eflags>>10)&1, \
           ($eflags>>11)&1
end

echo GDB assembly debugging configuration loaded
echo Commands: asm-layout, regs64, flags
EOF

# Create VS Code workspace configuration
mkdir -p .vscode

cat > .vscode/settings.json << 'EOF'
{
    "files.associations": {
        "*.s": "x86_64",
        "*.asm": "x86_64",
        "*.inc": "x86_64"
    },
    "C_Cpp.errorSquiggles": "Disabled",
    "C_Cpp.intelliSenseEngine": "Default",
    "terminal.integrated.cwd": "${workspaceFolder}/src"
}
EOF

cat > .vscode/tasks.json << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "build-assembly",
            "type": "shell",
            "command": "${workspaceFolder}/scripts/build_assembly.sh",
            "args": ["${file}"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "debug-assembly",
            "type": "shell",
            "command": "${workspaceFolder}/scripts/debug_assembly.sh",
            "args": ["${workspaceFolder}/build/${fileBasenameNoExtension}"],
            "group": "build",
            "dependsOn": "build-assembly",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "test-all-assembly",
            "type": "shell",
            "command": "${workspaceFolder}/scripts/test_assembly.sh",
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
EOF

cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Assembly (Current File)",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build/${fileBasenameNoExtension}",
            "args": [],
            "stopAtEntry": true,
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": false,
            "MIMode": "gdb",
            "miDebuggerPath": "/usr/bin/gdb",
            "setupCommands": [
                {
                    "description": "Load assembly GDB config",
                    "text": "source ${workspaceFolder}/tools/gdbinit_assembly",
                    "ignoreFailures": true
                },
                {
                    "description": "Enable pretty-printing",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ],
            "preLaunchTask": "build-assembly",
            "logging": {
                "engineLogging": false
            }
        }
    ]
}
EOF

# Copy hello.s to src directory if it exists
if [ -f "src/hello.s" ]; then
    cp src/hello.s src/hello.s
else
    # Create example hello.s
    cat > src/hello.s << 'EOF'
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
EOF
fi

echo ""
echo "=== Assembly Debugging Environment Setup Complete ==="
echo ""
echo "Workspace created at: ~/assembly-workspace"
echo ""
echo "Available scripts:"
echo "  scripts/build_assembly.sh  - Build assembly with debug info"
echo "  scripts/debug_assembly.sh  - Automated debugging session"
echo "  scripts/test_assembly.sh   - Test framework for assembly"
echo ""
echo "VS Code configuration:"
echo "  - Tasks configured for building and debugging"
echo "  - Launch configuration for GDB debugging"
echo "  - Assembly syntax highlighting enabled"
echo ""
echo "To get started:"
echo "  1. cd ~/assembly-workspace"
echo "  2. code .  # Open in VS Code"
echo "  3. Open src/hello.s"
echo "  4. Press Ctrl+Shift+P -> 'Tasks: Run Task' -> 'build-assembly'"
echo "  5. Press F5 to start debugging"
echo ""
echo "Or use command line:"
echo "  1. cd ~/assembly-workspace/src"
echo "  2. ../scripts/build_assembly.sh hello.s"
echo "  3. ../scripts/debug_assembly.sh ../build/hello"
echo ""
