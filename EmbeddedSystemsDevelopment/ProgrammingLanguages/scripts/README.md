# Scripts

This directory contains utility scripts for building, testing, and measuring performance of Qt, C++, and C applications.

## Available Scripts

### 1. `build_all.sh`
Builds all applications with various optimization levels.

```bash
# Build all applications
./scripts/build_all.sh

# Build specific language
./scripts/build_all.sh c
./scripts/build_all.sh cpp  
./scripts/build_all.sh qt

# Build with specific optimization
BUILD_TYPE=debug ./scripts/build_all.sh
BUILD_TYPE=static ./scripts/build_all.sh

# Cross-compile for ARM
./scripts/build_all.sh arm

# Clean all builds
./scripts/build_all.sh clean
```

### 2. `measure_performance.sh`
Comprehensive performance measurement and comparison tool.

```bash
# Full performance analysis
./scripts/measure_performance.sh

# Quick test
./scripts/measure_performance.sh --quick

# Skip build step
./scripts/measure_performance.sh --no-build
```

**Output includes:**
- Binary sizes
- Execution times (average, min, max)
- Memory usage (heap and stack)
- CPU performance metrics
- Detailed comparison report

### 3. `setup_devenv.sh`
Development environment setup script.

```bash
# Full installation
./scripts/setup_devenv.sh

# Install specific components
./scripts/setup_devenv.sh --basic    # Basic development tools
./scripts/setup_devenv.sh --qt       # Qt development tools
./scripts/setup_devenv.sh --perf     # Performance analysis tools
./scripts/setup_devenv.sh --cross    # Cross-compilation tools
```

**Installs:**
- Build tools (gcc, g++, make, cmake)
- Qt6 development libraries
- Performance analysis tools (valgrind, perf, gprof)
- Cross-compilation toolchains
- Additional development utilities

### 4. `demo.sh`
Interactive demonstration of all applications.

```bash
# Full demo with build
./scripts/demo.sh

# Quick demo
./scripts/demo.sh --quick

# Just build applications
./scripts/demo.sh --build-only
```

**Demonstrates:**
- Application compilation and execution
- Binary size comparison
- Library dependencies
- Performance characteristics
- RTOS optimization features

## Usage Examples

### Basic Workflow
```bash
# 1. Setup development environment
./scripts/setup_devenv.sh

# 2. Build all applications
./scripts/build_all.sh

# 3. Run demo
./scripts/demo.sh

# 4. Measure performance
./scripts/measure_performance.sh
```

### Development Workflow
```bash
# Debug builds for development
BUILD_TYPE=debug ./scripts/build_all.sh

# Test specific application
cd src/c && ./c_hello_world --perf
cd src/cpp && ./cpp_hello_world --info

# Cross-compile for target
./scripts/build_all.sh arm
```

### Performance Analysis Workflow
```bash
# Build optimized versions
BUILD_TYPE=release ./scripts/build_all.sh

# Run comprehensive benchmarks
./scripts/measure_performance.sh

# Check results
ls -la results/
```

## Script Features

### Error Handling
- All scripts include comprehensive error checking
- Graceful handling of missing dependencies
- Informative error messages and suggestions

### Cross-Platform Support
- Automatic OS detection (Ubuntu/Debian, CentOS/RHEL, Fedora)
- Package manager adaptation
- Fallback options for unsupported systems

### Performance Optimization
- Parallel builds using all CPU cores
- Optimized compiler flags
- Multiple optimization levels

## Troubleshooting

### Permission Issues
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Fix ownership if needed
sudo chown -R $USER:$USER .
```

### Missing Dependencies
```bash
# Install basic tools
sudo apt-get install build-essential cmake

# Install Qt6 (Ubuntu/Debian)
sudo apt-get install qt6-base-dev qt6-tools-dev

# Install performance tools
sudo apt-get install valgrind perf linux-tools-generic
```

### Build Failures
```bash
# Clean and rebuild
./scripts/build_all.sh clean
./scripts/build_all.sh

# Check environment
./scripts/setup_devenv.sh --help

# Manual build for debugging
cd src/c && make debug
```

### Performance Measurement Issues
```bash
# Check available tools
which valgrind perf time

# Run with reduced scope
./scripts/measure_performance.sh --quick

# Check system resources
htop
free -h
```
