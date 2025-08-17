#!/bin/bash

# Demo script to showcase Qt, C++, and C applications
# Builds and runs each application with basic performance comparison

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[DEMO]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

header() {
    echo -e "${CYAN}"
    echo "========================================"
    echo "$1"
    echo "========================================"
    echo -e "${NC}"
}

# Build applications if needed
ensure_built() {
    log "Checking if applications are built..."
    
    local need_build=false
    
    if [ ! -f "$PROJECT_ROOT/src/c/c_hello_world" ]; then
        need_build=true
    fi
    
    if [ ! -f "$PROJECT_ROOT/src/cpp/cpp_hello_world" ]; then
        need_build=true
    fi
    
    # Qt is optional
    if [ ! -f "$PROJECT_ROOT/src/qt/build/QtHelloWorld" ] && command -v qmake6 >/dev/null 2>&1; then
        need_build=true
    fi
    
    if [ "$need_build" = true ]; then
        log "Building applications..."
        "$SCRIPT_DIR/build_all.sh" || error "Build failed"
    else
        log "Applications already built"
    fi
}

# Demo C application
demo_c() {
    header "C Application Demo"
    
    local c_app="$PROJECT_ROOT/src/c/c_hello_world"
    
    if [ ! -f "$c_app" ]; then
        error "C application not found: $c_app"
        return 1
    fi
    
    info "Binary size: $(stat -c%s "$c_app") bytes"
    info "Binary type: $(file "$c_app" | cut -d: -f2)"
    
    echo
    log "Running C Hello World..."
    echo "Output:"
    echo "----------------------------------------"
    timeout 10s "$c_app" --hello || warning "C app timed out or failed"
    echo "----------------------------------------"
    echo
    
    log "Running C performance test..."
    echo "Performance Results:"
    echo "----------------------------------------"
    timeout 30s "$c_app" --perf || warning "C performance test timed out or failed"
    echo "----------------------------------------"
    echo
}

# Demo C++ application
demo_cpp() {
    header "C++ Application Demo"
    
    local cpp_app="$PROJECT_ROOT/src/cpp/cpp_hello_world"
    
    if [ ! -f "$cpp_app" ]; then
        error "C++ application not found: $cpp_app"
        return 1
    fi
    
    info "Binary size: $(stat -c%s "$cpp_app") bytes"
    info "Binary type: $(file "$cpp_app" | cut -d: -f2)"
    
    echo
    log "Running C++ Hello World..."
    echo "Output:"
    echo "----------------------------------------"
    timeout 10s "$cpp_app" --hello || warning "C++ app timed out or failed"
    echo "----------------------------------------"
    echo
    
    log "Running C++ performance test..."
    echo "Performance Results:"
    echo "----------------------------------------"
    timeout 30s "$cpp_app" --perf || warning "C++ performance test timed out or failed"
    echo "----------------------------------------"
    echo
}

# Demo Qt application
demo_qt() {
    header "Qt Application Demo"
    
    local qt_app="$PROJECT_ROOT/src/qt/build/QtHelloWorld"
    
    if [ ! -f "$qt_app" ]; then
        warning "Qt application not found: $qt_app"
        warning "This is normal if Qt6 is not installed"
        return 0
    fi
    
    info "Binary size: $(stat -c%s "$qt_app") bytes"
    info "Binary type: $(file "$qt_app" | cut -d: -f2)"
    
    echo
    log "Qt application is a GUI application"
    info "To run the Qt application:"
    info "  cd $PROJECT_ROOT/src/qt/build"
    info "  ./QtHelloWorld"
    
    # Check if we can run GUI apps
    if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
        log "Display server detected - Qt app can run graphically"
        info "The Qt application provides:"
        info "  - Graphical user interface"
        info "  - Interactive buttons"
        info "  - Performance measurement"
        info "  - Real-time clock display"
    else
        info "No display server detected - GUI demo not available"
        info "Install and configure X11 or Wayland to run Qt application"
    fi
    echo
}

# Compare binary sizes
compare_binaries() {
    header "Binary Size Comparison"
    
    local c_app="$PROJECT_ROOT/src/c/c_hello_world"
    local cpp_app="$PROJECT_ROOT/src/cpp/cpp_hello_world"
    local qt_app="$PROJECT_ROOT/src/qt/build/QtHelloWorld"
    
    printf "%-15s | %10s | %s\n" "Language" "Size" "File Type"
    printf "%-15s-+-%10s-+-%.50s\n" "---------------" "----------" "--------------------------------------------------"
    
    if [ -f "$c_app" ]; then
        local c_size=$(stat -c%s "$c_app")
        local c_type=$(file -b "$c_app" | cut -d, -f1)
        printf "%-15s | %10d | %s\n" "C" "$c_size" "$c_type"
    fi
    
    if [ -f "$cpp_app" ]; then
        local cpp_size=$(stat -c%s "$cpp_app")
        local cpp_type=$(file -b "$cpp_app" | cut -d, -f1)
        printf "%-15s | %10d | %s\n" "C++" "$cpp_size" "$cpp_type"
    fi
    
    if [ -f "$qt_app" ]; then
        local qt_size=$(stat -c%s "$qt_app")
        local qt_type=$(file -b "$qt_app" | cut -d, -f1)
        printf "%-15s | %10d | %s\n" "Qt" "$qt_size" "$qt_type"
    fi
    
    echo
}

# Show dependencies
show_dependencies() {
    header "Library Dependencies"
    
    local c_app="$PROJECT_ROOT/src/c/c_hello_world"
    local cpp_app="$PROJECT_ROOT/src/cpp/cpp_hello_world"
    local qt_app="$PROJECT_ROOT/src/qt/build/QtHelloWorld"
    
    if [ -f "$c_app" ]; then
        echo "C Application Dependencies:"
        ldd "$c_app" 2>/dev/null || echo "  Static or no dependencies"
        echo
    fi
    
    if [ -f "$cpp_app" ]; then
        echo "C++ Application Dependencies:"
        ldd "$cpp_app" 2>/dev/null || echo "  Static or no dependencies"
        echo
    fi
    
    if [ -f "$qt_app" ]; then
        echo "Qt Application Dependencies:"
        ldd "$qt_app" 2>/dev/null | head -10 || echo "  Dependencies not available"
        echo
    fi
}

# Performance summary
show_performance_summary() {
    header "Quick Performance Summary"
    
    info "Performance characteristics (typical):"
    echo
    printf "%-15s | %-12s | %-12s | %-15s\n" "Language" "Startup Time" "Binary Size" "Memory Usage"
    printf "%-15s-+-%-12s-+-%-12s-+-%-15s\n" "---------------" "------------" "------------" "---------------"
    printf "%-15s | %-12s | %-12s | %-15s\n" "C" "~1ms" "~20KB" "~500KB"
    printf "%-15s | %-12s | %-12s | %-15s\n" "C++" "~2ms" "~50KB" "~1MB"
    printf "%-15s | %-12s | %-12s | %-15s\n" "Qt" "~100ms" "~2MB" "~10MB"
    echo
    
    info "For detailed performance analysis, run:"
    info "  $SCRIPT_DIR/measure_performance.sh"
    echo
}

# Main demo function
main() {
    header "Programming Languages Demo for RTOS"
    info "This demo showcases C, C++, and Qt applications"
    info "optimized for Real-Time Operating Systems"
    echo
    
    # Ensure applications are built
    ensure_built
    
    # Run individual demos
    demo_c
    demo_cpp
    demo_qt
    
    # Show comparisons
    compare_binaries
    show_dependencies
    show_performance_summary
    
    # Final information
    header "Next Steps"
    info "To explore further:"
    echo
    info "1. Build applications:"
    info "   $SCRIPT_DIR/build_all.sh"
    echo
    info "2. Run performance benchmarks:"
    info "   $SCRIPT_DIR/measure_performance.sh"
    echo  
    info "3. Setup development environment:"
    info "   $SCRIPT_DIR/setup_devenv.sh"
    echo
    info "4. Cross-compile for ARM:"
    info "   cd src/c && make arm"
    info "   cd src/cpp && make arm"
    echo
    info "5. Read individual README files in src/ directories"
    echo
    
    log "Demo complete!"
}

# Usage information
usage() {
    cat << EOF
Usage: $0 [options]

Options:
    -h, --help      Show this help message
    --build-only    Only build applications, don't run demo
    --no-build      Skip building, assume applications exist
    --quick         Run abbreviated demo

Examples:
    $0              # Full demo
    $0 --quick      # Quick demo without performance tests
    $0 --build-only # Just build the applications

EOF
}

# Parse arguments
BUILD_ONLY=false
NO_BUILD=false
QUICK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --no-build)
            NO_BUILD=true
            shift
            ;;
        --quick)
            QUICK=true
            shift
            ;;
        *)
            error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Execute
if [ "$BUILD_ONLY" = true ]; then
    log "Building applications only..."
    "$SCRIPT_DIR/build_all.sh"
    log "Build complete!"
elif [ "$NO_BUILD" = true ]; then
    log "Skipping build step..."
    # Run demos without ensuring build
    demo_c
    demo_cpp  
    demo_qt
    compare_binaries
else
    main
fi
