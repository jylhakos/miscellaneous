# Qt Hello World

## Overview
This Qt application demonstrates a simple "Hello World" program optimized for RTOS deployment. It includes performance measurement capabilities and showcases Qt's event-driven architecture.

## Features
- Graphical user interface with Qt Widgets
- Performance benchmarking functionality
- Startup time measurement
- Real-time clock display
- Memory-efficient implementation

## Prerequisites
```bash
# Install Qt6 development packages on Debian/Ubuntu
sudo apt-get update
sudo apt-get install qt6-base-dev qt6-tools-dev cmake build-essential

# For cross-compilation (ARM example)
sudo apt-get install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
```

## Building

### Native Build (Linux/Debian)
```bash
# Create build directory
mkdir build && cd build

# Configure with CMake
cmake ..

# Build the application
make -j$(nproc)

# Run the application
./QtHelloWorld
```

### Release Build with Optimizations
```bash
mkdir build-release && cd build-release
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
```

### Cross-Compilation for ARM
```bash
# Set up cross-compilation environment
export CC=arm-linux-gnueabihf-gcc
export CXX=arm-linux-gnueabihf-g++

# Create cross-compilation build
mkdir build-arm && cd build-arm
cmake -DCMAKE_TOOLCHAIN_FILE=../arm-toolchain.cmake ..
make -j$(nproc)
```

## Performance

### Binary Size
- Debug build: ~2-3 MB (with Qt libraries)
- Release build: ~1-2 MB (with Qt libraries)
- Static build: ~15-20 MB (includes Qt libraries)

### Memory Usage
- Base memory footprint: ~10-15 MB
- Runtime heap usage: ~2-5 MB
- Stack usage per thread: ~8 KB

### Startup Time
- Cold start: ~200-500 ms
- Warm start: ~100-200 ms
- GUI initialization: ~50-100 ms

## Deployment

### Creating Deployment Package
```bash
# Install to deployment directory
cmake --install build --prefix deploy/qt_app

# The deployment script will automatically copy required Qt libraries
```

### RTOS Deployment Notes
- For RTOS deployment, consider using Qt for MCUs instead of full Qt
- Static linking reduces deployment complexity
- Memory usage should be monitored for resource-constrained systems
- Consider disabling unnecessary Qt modules for smaller footprint

## Performance Testing
The application includes a built-in performance test that:
- Performs 1,000,000 floating-point operations
- Measures execution time in microseconds
- Calculates operations per second
- Displays results in a dialog box

## Optimization Tips for RTOS
1. **Memory Management**: Avoid dynamic allocation in real-time paths
2. **Event Handling**: Use Qt's signal-slot mechanism for deterministic behavior
3. **Threading**: Utilize Qt's threading model with proper priorities
4. **Graphics**: Consider Qt Quick for hardware-accelerated rendering
5. **Startup Time**: Use static linking and minimize initialization code

## Troubleshooting

### Common Build Issues
```bash
# If Qt6 is not found
export CMAKE_PREFIX_PATH=/path/to/qt6

# If cross-compilation fails
sudo apt-get install qt6-tools-dev-tools

# For static builds
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF ..
```

### Runtime Issues
- Ensure all Qt libraries are present in deployment
- Check LD_LIBRARY_PATH for shared library builds
- Verify display server availability (X11/Wayland)
