#!/bin/bash

set -e

# Create necessary directories
mkdir -p build/{gcc,clang,analysis}

echo "=== Compiler Comparison for Embedded Development ==="

# Compile with different compilers and settings
echo "1. Compiling C program with different compilers..."

gcc -std=c99 -Wall -O2 -s src/C/t.c -o build/gcc/hello_c_gcc
clang -std=c99 -Wall -O2 -s src/C/t.c -o build/clang/hello_c_clang

echo "2. Compiling C++ program..."
g++ -std=c++17 -Wall -O2 -s src/C++/t.cpp -o build/gcc/hello_cpp_gcc
clang++ -std=c++17 -Wall -O2 -s src/C++/t.cpp -o build/clang/hello_cpp_clang

echo "3. Size comparison:"
echo "GCC C binary size:   $(stat -c%s build/gcc/hello_c_gcc) bytes"
echo "Clang C binary size: $(stat -c%s build/clang/hello_c_clang) bytes"
echo "GCC C++ binary size:   $(stat -c%s build/gcc/hello_cpp_gcc) bytes" 
echo "Clang C++ binary size: $(stat -c%s build/clang/hello_cpp_clang) bytes"

echo "4. Performance test (simple execution time):"
echo -n "GCC C program: "
time ./build/gcc/hello_c_gcc >/dev/null

echo -n "Clang C program: "
time ./build/clang/hello_c_clang >/dev/null

echo "5. Generate analysis files:"
# Generate LLVM IR
clang -S -emit-llvm -O2 src/C/t.c -o build/analysis/t.ll

# Generate assembly for comparison
gcc -S -O2 src/C/t.c -o build/analysis/t_gcc.s
clang -S -O2 src/C/t.c -o build/analysis/t_clang.s

echo "Analysis files generated in build/analysis/"
echo "=== Comparison Complete ==="
