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
