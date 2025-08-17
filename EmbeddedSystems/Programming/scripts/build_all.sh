#!/bin/bash

# Build All Applications Script: Builds Qt, C++, and C applications with various optimization levels

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_ROOT/src"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Build C application
build_c() {
    log "Building C application..."
    cd "$SRC_DIR/c"
    
    make clean >/dev/null 2>&1 || true
    
    case ${BUILD_TYPE:-release} in
        debug)
            make debug
            ;;
        release)
            make release
            ;;
        static)
            make static
            ;;
        minimal)
            make minimal
            ;;
        *)
            make
            ;;
    esac
    
    if [ -f "c_hello_world" ]; then
        log "C build successful"
        ls -lh c_hello_world
    else
        error "C build failed"
        return 1
    fi
}

# Build C++ application  
build_cpp() {
    log "Building C++ application..."
    cd "$SRC_DIR/cpp"
    
    make clean >/dev/null 2>&1 || true
    
    case ${BUILD_TYPE:-release} in
        debug)
            make debug
            ;;
        release)
            make release
            ;;
        static)
            make static
            ;;
        *)
            make
            ;;
    esac
    
    if [ -f "cpp_hello_world" ]; then
        log "C++ build successful"
        ls -lh cpp_hello_world
    else
        error "C++ build failed"
        return 1
    fi
}

# Build Qt application
build_qt() {
    log "Building Qt application..."
    cd "$SRC_DIR/qt"
    
    # Check if Qt6 is available
    if ! command -v qmake6 >/dev/null 2>&1 && ! command -v qt6-config >/dev/null 2>&1; then
        warning "Qt6 not found. Install with: sudo apt-get install qt6-base-dev qt6-tools-dev"
        return 0
    fi
    
    rm -rf build >/dev/null 2>&1 || true
    mkdir -p build
    cd build
    
    case ${BUILD_TYPE:-release} in
        debug)
            cmake -DCMAKE_BUILD_TYPE=Debug ..
            ;;
        *)
            cmake -DCMAKE_BUILD_TYPE=Release ..
            ;;
    esac
    
    make -j$(nproc)
    
    if [ -f "QtHelloWorld" ]; then
        log "Qt build successful"
        ls -lh QtHelloWorld
    else
        error "Qt build failed"
        return 1
    fi
}

# Build Assembly application
build_assembly() {
    log "Building Assembly application..."
    cd "$SRC_DIR/assembler"
    
    # Check if NASM is available
    if ! command -v nasm >/dev/null 2>&1; then
        warning "NASM not found. Install with: sudo apt-get install nasm"
        return 0
    fi
    
    make clean >/dev/null 2>&1 || true
    
    case ${BUILD_TYPE:-release} in
        debug)
            make debug
            ;;
        release)
            make release
            ;;
        static)
            make static
            ;;
        *)
            make
            ;;
    esac
    
    if [ -f "hello_world" ] || [ -f "hello_world_debug" ]; then
        log "Assembly build successful"
        ls -lh hello_world* 2>/dev/null || true
    else
        error "Assembly build failed"
        return 1
    fi
}

# Build all applications
build_all() {
    log "Starting build process for all applications..."
    
    local failed=()
    
    if ! build_c; then
        failed+=("C")
    fi
    
    if ! build_cpp; then
        failed+=("C++")
    fi
    
    if ! build_assembly; then
        failed+=("Assembly")
    fi
    
    if ! build_qt; then
        failed+=("Qt")
    fi
    
    if [ ${#failed[@]} -eq 0 ]; then
        log "All builds completed successfully!"
    else
        warning "Some builds failed: ${failed[*]}"
        return 1
    fi
}

# Cross-compile for ARM
build_arm() {
    log "Cross-compiling for ARM..."
    
    # Check for ARM cross-compiler
    if ! command -v arm-linux-gnueabihf-gcc >/dev/null 2>&1; then
        warning "ARM cross-compiler not found. Install with:"
        warning "  sudo apt-get install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf"
        return 0
    fi
    
    # Build C for ARM
    cd "$SRC_DIR/c"
    make arm
    if [ -f "c_hello_world_arm" ]; then
        log "ARM C build successful"
        file c_hello_world_arm
    fi
    
    # Build C++ for ARM
    cd "$SRC_DIR/cpp"
    make arm
    if [ -f "cpp_hello_world_arm" ]; then
        log "ARM C++ build successful"
        file cpp_hello_world_arm
    fi
}

# Clean all builds
clean_all() {
    log "Cleaning all build artifacts..."
    
    cd "$SRC_DIR/c"
    make clean >/dev/null 2>&1 || true
    
    cd "$SRC_DIR/cpp"
    make clean >/dev/null 2>&1 || true
    
    cd "$SRC_DIR/assembler"
    make clean >/dev/null 2>&1 || true
    
    cd "$SRC_DIR/qt"
    rm -rf build >/dev/null 2>&1 || true
    
    log "Clean complete"
}

# Show usage
usage() {
    cat << EOF
Usage: $0 [options] [targets]

Targets:
    all     Build all applications (default)
    c       Build C application only
    cpp     Build C++ application only
    asm     Build Assembly application only
    qt      Build Qt application only
    arm     Cross-compile for ARM
    clean   Clean all build artifacts

Build Types (set BUILD_TYPE environment variable):
    debug   Debug build with symbols
    release Release build with optimizations (default)
    static  Static linking
    minimal Minimal size build (C only)

Options:
    -h, --help      Show this help
    -v, --verbose   Verbose output
    -j, --jobs N    Use N parallel jobs

Examples:
    $0                      # Build all applications
    $0 c cpp asm           # Build only C, C++ and Assembly
    $0 clean               # Clean all builds
    BUILD_TYPE=debug $0    # Build all in debug mode
    $0 arm                 # Cross-compile for ARM

EOF
}

# Main function
main() {
    local targets=("all")
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -v|--verbose)
                set -x
                shift
                ;;
            -j|--jobs)
                export MAKEFLAGS="-j$2"
                shift 2
                ;;
            clean|c|cpp|asm|qt|all|arm)
                if [ "$1" != "all" ]; then
                    targets=("$1")
                fi
                shift
                ;;
            *)
                error "Unknown argument: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Execute targets
    for target in "${targets[@]}"; do
        case $target in
            all)
                build_all
                ;;
            c)
                build_c
                ;;
            cpp)
                build_cpp
                ;;
            asm)
                build_assembly
                ;;
            qt)
                build_qt
                ;;
            arm)
                build_arm
                ;;
            clean)
                clean_all
                ;;
        esac
    done
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
