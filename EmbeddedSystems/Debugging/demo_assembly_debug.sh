#!/bin/bash
# Demo: Assembly Debugging with hello.s
# This script demonstrates step-by-step assembly debugging

set -e
cd "$(dirname "$0")"

echo "=== Assembly Debugging Demonstration with hello.s ==="
echo "This demo shows how to debug assembly code using various tools"
echo ""

# Build hello.s with debug symbols
echo "1. Building hello.s with debug symbols..."
echo "Command: as --64 --gstabs+ --gdwarf-4 src/hello.s -o hello.o"
as --64 --gstabs+ --gdwarf-4 src/hello.s -o hello.o

echo "Command: ld hello.o -o hello"
ld hello.o -o hello

echo "✓ Build complete!"
echo ""

# Verify debug symbols
echo "2. Verifying debug symbols..."
echo "Debug sections in the binary:"
objdump -h hello | grep debug || echo "No debug sections found (this is normal for simple assembly)"
echo ""

# Show binary information
echo "3. Binary information:"
file hello
size hello
echo ""

# Disassemble the program
echo "4. Disassembling the program:"
echo "Command: objdump -d hello"
objdump -d hello
echo ""

# Show symbols
echo "5. Symbol table:"
echo "Command: nm hello"
nm hello
echo ""

# System call analysis
echo "6. System call analysis:"
echo "Command: strace ./hello"
echo "Running program with strace to show system calls..."
strace ./hello 2>&1 | head -20
echo ""

# Create GDB debugging script
echo "7. Creating automated GDB debugging session..."
cat > debug_session.gdb << 'EOF'
# Automated GDB debugging session for hello.s
set disassembly-flavor intel
set logging file gdb_debug.log
set logging overwrite on
set logging on

file hello
echo === Loading hello executable ===\n

# Show file information
info file

# Disassemble _start function
echo === Disassembling _start function ===\n
disas _start

# Set breakpoint at _start
break _start
echo === Breakpoint set at _start ===\n

# Start the program
run
echo === Program started, stopped at _start ===\n

# Show current registers
echo === Initial register state ===\n
info registers

# Show next few instructions
echo === Next instructions ===\n
x/10i $rip

# Step through first instruction (mov $1, %rax)
stepi
echo === After first instruction (mov $1, %rax) ===\n
info registers rax
print/x $rax

# Step through second instruction (mov $1, %rdi)
stepi
echo === After second instruction (mov $1, %rdi) ===\n
info registers rdi
print/x $rdi

# Step through third instruction (mov hello_msg, %rsi)
stepi
echo === After third instruction (mov hello_msg, %rsi) ===\n
info registers rsi
print/x $rsi
x/s $rsi

# Step through fourth instruction (mov hello_len, %rdx)
stepi
echo === After fourth instruction (mov hello_len, %rdx) ===\n
info registers rdx
print/x $rdx

# Continue to see the output
echo === Continuing execution to see output ===\n
continue

# Program should finish here
echo === Program completed ===\n
quit
EOF

echo "Command: gdb -batch -x debug_session.gdb"
gdb -batch -x debug_session.gdb

echo ""
echo "8. GDB debugging session complete!"
echo "   Check gdb_debug.log for detailed debugging output"
echo ""

# Show memory layout
echo "9. Memory layout analysis:"
echo "Command: readelf -l hello"
readelf -l hello
echo ""

# Hexdump of the binary
echo "10. Hexdump of data section (first 64 bytes):"
echo "Command: hexdump -C hello | head -10"
hexdump -C hello | head -10
echo ""

# Performance measurement
echo "11. Performance measurement:"
echo "Command: time ./hello"
echo "Measuring execution time..."
time ./hello 2>&1 | grep real
echo ""

# Advanced: Show instruction encoding
echo "12. Instruction encoding analysis:"
echo "Command: objdump -d hello | grep -A5 '_start:'"
objdump -d hello | grep -A10 '_start:'
echo ""

# Show string data
echo "13. String data in binary:"
echo "Command: strings hello"
strings hello
echo ""

# VS Code debugging instructions
echo "=== VS Code Debugging Instructions ==="
echo ""
echo "To debug this assembly file in VS Code:"
echo "1. Open VS Code in this directory: code ."
echo "2. Open src/hello.s"
echo "3. Set a breakpoint by clicking on line number next to '_start:'"
echo "4. Press F5 or go to Run -> Start Debugging"
echo "5. Use the Debug Console to execute GDB commands:"
echo "   -exec info registers"
echo "   -exec x/10i \$rip"
echo "   -exec print \$rax"
echo "6. Use F10 to step over instructions"
echo "7. Use F11 to step into (same as step over for assembly)"
echo "8. Watch the Variables panel to see register values"
echo ""

# Clean up
echo "Cleaning up temporary files..."
rm -f debug_session.gdb gdb_debug.log

echo "=== Assembly Debugging Demonstration Complete ==="
echo ""
echo "Key debugging techniques demonstrated:"
echo "✓ Building with debug symbols"
echo "✓ Binary analysis with objdump, nm, readelf"
echo "✓ System call tracing with strace"
echo "✓ Automated GDB debugging session"
echo "✓ Memory and performance analysis"
echo "✓ VS Code integration instructions"
echo ""
echo "The hello program has been built and is ready for debugging!"
echo "Try: gdb ./hello"
echo ""
