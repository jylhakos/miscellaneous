#!/bin/bash
# compiler_check.sh - Comprehensive compiler detection and validation

echo "  Compiler Detection and Validation Report"
echo "==========================================="

# Function to check command availability
check_command() {
    local cmd="$1"
    local name="$2"
    if command -v "$cmd" >/dev/null 2>&1; then
        local version=$($cmd --version 2>/dev/null | head -n1)
        echo "  $name: $version"
        return 0
    else
        echo "❌ $name: Not found"
        return 1
    fi
}

# Function to check compiler standards support
check_standards() {
    local compiler="$1"
    local lang="$2"
    local std="$3"
    local test_file="/tmp/test_${lang}_${std}.${lang}"
    
    if [ "$lang" = "c" ]; then
        echo 'int main(){return 0;}' > "$test_file"
        if $compiler -std=$std -c "$test_file" -o "/tmp/test_${std}.o" 2>/dev/null; then
            echo "    $std support: Available"
            rm -f "/tmp/test_${std}.o"
        else
            echo "  ❌ $std support: Not available"
        fi
    elif [ "$lang" = "cpp" ]; then
        echo 'int main(){return 0;}' > "$test_file"
        if $compiler -std=$std -c "$test_file" -o "/tmp/test_${std}.o" 2>/dev/null; then
            echo "    $std support: Available"
            rm -f "/tmp/test_${std}.o"
        else
            echo "  ❌ $std support: Not available"
        fi
    fi
    rm -f "$test_file"
}

echo ""
echo "📋 Native Compilers:"
echo "-------------------"

# GCC Detection
if check_command "gcc" "GCC C Compiler"; then
    check_standards "gcc" "c" "c99"
    check_standards "gcc" "c" "c11"
    check_standards "gcc" "c" "c17"
fi

if check_command "g++" "GCC C++ Compiler"; then
    check_standards "g++" "cpp" "c++11"
    check_standards "g++" "cpp" "c++14"
    check_standards "g++" "cpp" "c++17"
    check_standards "g++" "cpp" "c++20"
fi

echo ""
echo "⚡ Clang/LLVM Toolchain:"
echo "----------------------"

# Clang Detection
if check_command "clang" "Clang C Compiler"; then
    check_standards "clang" "c" "c99"
    check_standards "clang" "c" "c11"
    check_standards "clang" "c" "c17"
fi

if check_command "clang++" "Clang C++ Compiler"; then
    check_standards "clang++" "cpp" "c++11"
    check_standards "clang++" "cpp" "c++14"
    check_standards "clang++" "cpp" "c++17"
    check_standards "clang++" "cpp" "c++20"
    
    # Check for libc++ support
    echo 'int main(){return 0;}' > /tmp/test_libcxx.cpp
    if clang++ -stdlib=libc++ -c /tmp/test_libcxx.cpp -o /tmp/test_libcxx.o 2>/dev/null; then
        echo "    libc++ support: Available"
        rm -f /tmp/test_libcxx.o
    else
        echo "  ❌ libc++ support: Not available"
    fi
    rm -f /tmp/test_libcxx.cpp
fi

echo ""
echo "🛠️ LLVM Development Tools:"
echo "-------------------------"
check_command "llvm-config" "LLVM Config"
check_command "lldb" "LLVM Debugger"
check_command "lld" "LLVM Linker"
check_command "llvm-ar" "LLVM Archiver"
check_command "llvm-objdump" "LLVM Object Dump"
check_command "llvm-strip" "LLVM Strip"

echo ""
echo "  Cross-Compilation Toolchains:"
echo "-------------------------------"
check_command "aarch64-linux-gnu-gcc" "ARM64 GCC"
check_command "aarch64-linux-gnu-g++" "ARM64 G++"
check_command "arm-linux-gnueabihf-gcc" "ARM Hard Float GCC"
check_command "arm-linux-gnueabihf-g++" "ARM Hard Float G++"

echo ""
echo "🔧 Build Tools:"
echo "-------------"
check_command "make" "GNU Make"
check_command "cmake" "CMake"
check_command "ninja" "Ninja Build"
check_command "autotools" "Autotools"
check_command "pkg-config" "pkg-config"

echo ""
echo "  System Information:"
echo "--------------------"
echo "OS: $(uname -s)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
echo "CPU Cores: $(nproc)"
echo "Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo "Disk Space (current dir): $(df -h . | awk 'NR==2 {print $4 " available"}')"

echo ""
echo "🧪 Compilation Tests:"
echo "-------------------"

# Create test files
cat > /tmp/test_c99.c << 'EOF'
#include <stdio.h>
#include <complex.h>
int main() {
    double complex z = 1.0 + 2.0*I;
    printf("C99 complex number: %.1f + %.1fi\n", creal(z), cimag(z));
    return 0;
}
EOF

cat > /tmp/test_cpp17.cpp << 'EOF'
#include <iostream>
#include <optional>
#include <string_view>
int main() {
    std::optional<std::string_view> msg = "C++17 features working";
    if (msg) {
        std::cout << *msg << std::endl;
    }
    return 0;
}
EOF

# Test C99 compilation
if command -v gcc >/dev/null 2>&1; then
    if gcc -std=c99 /tmp/test_c99.c -o /tmp/test_c99 -lm 2>/dev/null; then
        if /tmp/test_c99 >/dev/null 2>&1; then
            echo "  GCC C99 compilation and execution: Working"
        else
            echo "⚠️  GCC C99 compilation: OK, execution: Failed"
        fi
        rm -f /tmp/test_c99
    else
        echo "❌ GCC C99 compilation: Failed"
    fi
fi

if command -v clang >/dev/null 2>&1; then
    if clang -std=c99 /tmp/test_c99.c -o /tmp/test_c99_clang -lm 2>/dev/null; then
        if /tmp/test_c99_clang >/dev/null 2>&1; then
            echo "  Clang C99 compilation and execution: Working"
        else
            echo "⚠️  Clang C99 compilation: OK, execution: Failed"
        fi
        rm -f /tmp/test_c99_clang
    else
        echo "❌ Clang C99 compilation: Failed"
    fi
fi

# Test C++17 compilation
if command -v g++ >/dev/null 2>&1; then
    if g++ -std=c++17 /tmp/test_cpp17.cpp -o /tmp/test_cpp17 2>/dev/null; then
        if /tmp/test_cpp17 >/dev/null 2>&1; then
            echo "  G++ C++17 compilation and execution: Working"
        else
            echo "⚠️  G++ C++17 compilation: OK, execution: Failed"
        fi
        rm -f /tmp/test_cpp17
    else
        echo "❌ G++ C++17 compilation: Failed"
    fi
fi

if command -v clang++ >/dev/null 2>&1; then
    if clang++ -std=c++17 /tmp/test_cpp17.cpp -o /tmp/test_cpp17_clang 2>/dev/null; then
        if /tmp/test_cpp17_clang >/dev/null 2>&1; then
            echo "  Clang++ C++17 compilation and execution: Working"
        else
            echo "⚠️  Clang++ C++17 compilation: OK, execution: Failed"
        fi
        rm -f /tmp/test_cpp17_clang
    else
        echo "❌ Clang++ C++17 compilation: Failed"
    fi
    
    # Test with libc++
    if clang++ -std=c++17 -stdlib=libc++ /tmp/test_cpp17.cpp -o /tmp/test_cpp17_libcxx 2>/dev/null; then
        if /tmp/test_cpp17_libcxx >/dev/null 2>&1; then
            echo "  Clang++ C++17 with libc++: Working"
        else
            echo "⚠️  Clang++ C++17 with libc++: Compiled, execution failed"
        fi
        rm -f /tmp/test_cpp17_libcxx
    else
        echo "❌ Clang++ C++17 with libc++: Failed"
    fi
fi

# Cleanup test files
rm -f /tmp/test_c99.c /tmp/test_cpp17.cpp

echo ""
echo "📦 Installation Recommendations:"
echo "------------------------------"
if ! command -v gcc >/dev/null 2>&1 || ! command -v g++ >/dev/null 2>&1; then
    echo "Install GCC:"
    command -v apt >/dev/null 2>&1 && echo "  sudo apt install gcc g++ build-essential"
    command -v dnf >/dev/null 2>&1 && echo "  sudo dnf install gcc gcc-c++ make"
    command -v yum >/dev/null 2>&1 && echo "  sudo yum install gcc gcc-c++ make"
fi

if ! command -v clang >/dev/null 2>&1 || ! command -v clang++ >/dev/null 2>&1; then
    echo "Install Clang/LLVM:"
    command -v apt >/dev/null 2>&1 && echo "  sudo apt install clang clang++ llvm-dev"
    command -v dnf >/dev/null 2>&1 && echo "  sudo dnf install clang clang++ llvm-devel"
    command -v yum >/dev/null 2>&1 && echo "  sudo yum install clang clang++ llvm-devel"
fi

echo ""
echo "🏁 Detection Complete!"
echo "===================="
