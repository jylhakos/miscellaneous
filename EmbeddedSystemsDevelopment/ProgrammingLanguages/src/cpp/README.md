# C++ Hello World

## Overview
This C++ application demonstrates modern C++17 features optimized for RTOS deployment. It includes comprehensive performance benchmarking and system information display capabilities.

## Features
- Interactive command-line interface
- Multiple performance benchmark tests
- System information reporting
- Command-line argument processing
- RTOS-optimized memory management
- Cross-platform compatibility

## Prerequisites
```bash
# Install build tools on Debian/Ubuntu
sudo apt-get update
sudo apt-get install build-essential g++ make

# For cross-compilation (ARM example)
sudo apt-get install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

# For profiling
sudo apt-get install gprof valgrind linux-perf
```

## Building

### Quick Build
```bash
# Default optimized build
make

# Run the application
make run
```

### Build Variations
```bash
# Debug build (no optimization, debug symbols)
make debug

# Release build (maximum optimization)
make release

# Static build (for deployment without dependencies)
make static

# Cross-compile for ARM
make arm

# Profiling build (for performance analysis)
make profile
```

### Manual Compilation
```bash
# Basic compilation
g++ -std=c++17 -O2 -o cpp_hello_world main.cpp

# With all warnings and debugging
g++ -std=c++17 -Wall -Wextra -g -O2 -o cpp_hello_world main.cpp

# Static linking for RTOS deployment
g++ -std=c++17 -O2 -static -o cpp_hello_world main.cpp
```

## Usage

### Interactive Mode (Default)
```bash
./cpp_hello_world
```
Displays a menu with options to:
1. Display Hello Message
2. Run Performance Test
3. Display System Info
4. Exit

### Command-Line Options
```bash
# Display hello message only
./cpp_hello_world --hello

# Run performance benchmark
./cpp_hello_world --perf

# Show system information
./cpp_hello_world --info

# Display help
./cpp_hello_world --help
```

## Performance

### Binary Size
- Debug build: ~50-100 KB
- Release build: ~30-50 KB
- Static build: ~2-3 MB

### Memory Usage
- Base memory footprint: ~1-2 MB
- Runtime heap usage: ~100 KB - 1 MB (depending on tests)
- Stack usage: ~8 KB

### Performance Benchmarks
The application includes three built-in benchmarks:

1. **Integer Operations**: Simple arithmetic operations
2. **Floating-Point Operations**: Trigonometric functions (sin/cos)
3. **Memory Operations**: Vector allocation and access patterns

### Typical Results (on modern x86_64)
- Integer operations: ~100-500 million ops/sec
- Floating-point operations: ~10-50 million ops/sec
- Memory operations: ~1-10 million ops/sec

## RTOS Optimization Features

### Memory Management
- No dynamic allocation in performance-critical paths
- Stack-based objects where possible
- Minimal STL usage in real-time contexts

### Performance Considerations
- Compile-time optimizations enabled
- Inlined functions for critical paths
- Efficient data structures
- Predictable execution times

### Real-Time Characteristics
- Deterministic execution paths
- Minimal system call overhead
- Low interrupt latency impact
- Bounded memory usage

## Cross-Compilation

### ARM Linux Example
```bash
# Set cross-compiler
export CXX=arm-linux-gnueabihf-g++

# Compile for ARM
make arm

# Verify binary
file cpp_hello_world_arm
```

### Custom Toolchain
```bash
# Set custom toolchain
export CXX=/path/to/custom-g++
export CXXFLAGS="-mcpu=cortex-m4 -mthumb"

# Build with custom flags
make CXXFLAGS="$CXXFLAGS"
```

## Performance Analysis

### Using gprof
```bash
# Build with profiling
make profile

# Run application
./cpp_hello_world --perf

# Generate profile report
gprof ./cpp_hello_world gmon.out > profile.txt
```

### Using Valgrind
```bash
# Memory analysis
valgrind --tool=memcheck ./cpp_hello_world --perf

# Performance analysis
valgrind --tool=callgrind ./cpp_hello_world --perf
```

### Using perf
```bash
# CPU performance monitoring
perf stat ./cpp_hello_world --perf

# Detailed profiling
perf record ./cpp_hello_world --perf
perf report
```

## Deployment

### Creating Deployment Package
```bash
# Build optimized static binary
make deploy

# Files will be in deploy/ directory
ls -la deploy/
```

### RTOS Deployment
- Use static linking to avoid library dependencies
- Consider memory constraints when sizing buffers
- Test real-time performance on target hardware
- Profile for worst-case execution time (WCET)

## Troubleshooting

### Build Issues
```bash
# If C++17 is not supported
g++ -std=c++14 -o cpp_hello_world main.cpp

# For older compilers
g++ -std=c++11 -o cpp_hello_world main.cpp
```

### Runtime Issues
```bash
# Check binary dependencies
ldd cpp_hello_world

# Run with debugging
gdb ./cpp_hello_world
```

### Performance Issues
```bash
# Check CPU scaling
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Disable CPU scaling for consistent results
sudo cpufreq-set -g performance
```
