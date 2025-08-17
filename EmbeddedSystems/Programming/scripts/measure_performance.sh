#!/bin/bash

# Performance Measurement Script for Qt, C++, and C Applications
# Compares execution time, memory usage, and system resource consumption

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_ROOT/src"
RESULTS_DIR="$PROJECT_ROOT/results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if required tools are installed
check_tools() {
    local missing_tools=()
    
    # Essential build tools
    command -v gcc >/dev/null 2>&1 || missing_tools+=("gcc")
    command -v g++ >/dev/null 2>&1 || missing_tools+=("g++")
    command -v make >/dev/null 2>&1 || missing_tools+=("make")
    command -v cmake >/dev/null 2>&1 || missing_tools+=("cmake")
    
    # Performance measurement tools
    command -v time >/dev/null 2>&1 || missing_tools+=("time")
    command -v perf >/dev/null 2>&1 || missing_tools+=("perf")
    command -v valgrind >/dev/null 2>&1 || missing_tools+=("valgrind")
    
    # Optional tools
    if ! command -v htop >/dev/null 2>&1; then
        warning "htop not found - system monitoring will be limited"
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        error "Missing required tools: ${missing_tools[*]}"
        info "Install missing tools:"
        info "  Ubuntu/Debian: sudo apt-get install build-essential cmake valgrind linux-tools-generic"
        info "  CentOS/RHEL: sudo yum install gcc gcc-c++ make cmake valgrind perf"
        return 1
    fi
    
    log "All required tools are available"
}

# Create results directory
setup_results_dir() {
    mkdir -p "$RESULTS_DIR"
    log "Results will be saved to: $RESULTS_DIR"
}

# Build all applications
build_applications() {
    log "Building all applications..."
    
    # Build C application
    info "Building C application..."
    cd "$SRC_DIR/c"
    make clean >/dev/null 2>&1 || true
    make release
    if [ ! -f "c_hello_world" ]; then
        error "Failed to build C application"
        return 1
    fi
    
    # Build C++ application
    info "Building C++ application..."
    cd "$SRC_DIR/cpp"
    make clean >/dev/null 2>&1 || true
    make release
    if [ ! -f "cpp_hello_world" ]; then
        error "Failed to build C++ application"
        return 1
    fi
    
    # Build Qt application
    info "Building Qt application..."
    cd "$SRC_DIR/qt"
    rm -rf build >/dev/null 2>&1 || true
    mkdir -p build
    cd build
    if command -v qt6-config >/dev/null 2>&1; then
        cmake -DCMAKE_BUILD_TYPE=Release ..
        make -j$(nproc)
    else
        warning "Qt6 not found - skipping Qt build"
        warning "Install Qt6: sudo apt-get install qt6-base-dev"
        return 0
    fi
    
    if [ ! -f "QtHelloWorld" ]; then
        warning "Qt application build failed - continuing without Qt tests"
    fi
    
    log "Build complete"
}

# Get binary size
get_binary_size() {
    local binary=$1
    if [ -f "$binary" ]; then
        stat -c%s "$binary"
    else
        echo "0"
    fi
}

# Measure execution time
measure_execution_time() {
    local binary=$1
    local args=$2
    local iterations=$3
    
    local total_time=0
    local min_time=999999
    local max_time=0
    
    for ((i=1; i<=iterations; i++)); do
        local time_output
        time_output=$( { /usr/bin/time -f "%e" $binary $args >/dev/null 2>&1; } 2>&1 )
        local exec_time
        exec_time=$(echo "$time_output" | tail -1)
        
        # Convert to milliseconds for easier handling
        local time_ms
        time_ms=$(echo "$exec_time * 1000" | bc -l 2>/dev/null || echo "$exec_time")
        
        total_time=$(echo "$total_time + $time_ms" | bc -l 2>/dev/null || echo "$total_time")
        
        # Update min/max
        if (( $(echo "$time_ms < $min_time" | bc -l 2>/dev/null || echo "0") )); then
            min_time=$time_ms
        fi
        if (( $(echo "$time_ms > $max_time" | bc -l 2>/dev/null || echo "0") )); then
            max_time=$time_ms
        fi
    done
    
    local avg_time
    avg_time=$(echo "scale=2; $total_time / $iterations" | bc -l 2>/dev/null || echo "0")
    
    echo "$avg_time $min_time $max_time"
}

# Measure memory usage with Valgrind
measure_memory_usage() {
    local binary=$1
    local args=$2
    local timeout_duration=30
    
    local temp_file=$(mktemp)
    
    # Run with timeout to prevent hanging
    if timeout $timeout_duration valgrind --tool=massif --stacks=yes --massif-out-file="$temp_file" \
       "$binary" $args >/dev/null 2>&1; then
        
        if [ -f "$temp_file" ]; then
            # Parse peak memory usage
            local peak_mem
            peak_mem=$(grep "^mem_heap_B=" "$temp_file" | sort -t'=' -k2 -n | tail -1 | cut -d'=' -f2)
            local peak_stack
            peak_stack=$(grep "^mem_stacks_B=" "$temp_file" | sort -t'=' -k2 -n | tail -1 | cut -d'=' -f2)
            
            echo "${peak_mem:-0} ${peak_stack:-0}"
        else
            echo "0 0"
        fi
    else
        warning "Memory measurement timed out for $binary"
        echo "0 0"
    fi
    
    rm -f "$temp_file"
}

# Performance test runner
run_performance_test() {
    local name=$1
    local binary=$2
    local args=$3
    
    info "Testing $name..."
    
    if [ ! -f "$binary" ]; then
        warning "$name binary not found: $binary"
        return
    fi
    
    # Basic info
    local binary_size
    binary_size=$(get_binary_size "$binary")
    
    # Execution time (5 iterations)
    local time_results
    time_results=$(measure_execution_time "$binary" "$args" 5)
    local avg_time min_time max_time
    read -r avg_time min_time max_time <<< "$time_results"
    
    # Memory usage
    local memory_results
    memory_results=$(measure_memory_usage "$binary" "$args")
    local peak_heap peak_stack
    read -r peak_heap peak_stack <<< "$memory_results"
    
    # Output results
    printf "%-15s | %8d | %8.2f | %8.2f | %8.2f | %10d | %10d\n" \
           "$name" "$binary_size" "$avg_time" "$min_time" "$max_time" "$peak_heap" "$peak_stack"
}

# CPU performance test
run_cpu_performance_test() {
    local name=$1
    local binary=$2
    
    info "CPU performance test for $name..."
    
    if [ ! -f "$binary" ]; then
        warning "$name binary not found: $binary"
        return
    fi
    
    # Use perf if available, otherwise fall back to time
    if command -v perf >/dev/null 2>&1; then
        local perf_output
        perf_output=$(perf stat -e cycles,instructions,cache-misses,branch-misses \
                     "$binary" --perf 2>&1 | grep -E "(cycles|instructions|cache-misses|branch-misses)")
        
        echo "=== $name CPU Performance ==="
        echo "$perf_output"
        echo ""
    else
        warning "perf not available, using basic timing"
        /usr/bin/time -v "$binary" --perf >/dev/null
    fi
}

# Generate comparison report
generate_report() {
    local report_file="$RESULTS_DIR/performance_report_$TIMESTAMP.txt"
    
    {
        echo "Performance Comparison Report"
        echo "Generated: $(date)"
        echo "System: $(uname -a)"
        echo "CPU: $(cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d':' -f2 | xargs)"
        echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
        echo "=================================================="
        echo ""
        
        echo "Binary Size and Basic Performance:"
        printf "%-15s | %8s | %8s | %8s | %8s | %10s | %10s\n" \
               "Language" "Size(B)" "Avg(ms)" "Min(ms)" "Max(ms)" "Heap(B)" "Stack(B)"
        printf "%-15s-+-%8s-+-%8s-+-%8s-+-%8s-+-%10s-+-%10s\n" \
               "---------------" "--------" "--------" "--------" "--------" "----------" "----------"
        
        run_performance_test "C" "$SRC_DIR/c/c_hello_world" "--perf"
        run_performance_test "C++" "$SRC_DIR/cpp/cpp_hello_world" "--perf"
        if [ -f "$SRC_DIR/qt/build/QtHelloWorld" ]; then
            run_performance_test "Qt" "$SRC_DIR/qt/build/QtHelloWorld" ""
        fi
        
        echo ""
        echo "Detailed CPU Performance:"
        echo "========================="
        
        run_cpu_performance_test "C" "$SRC_DIR/c/c_hello_world"
        run_cpu_performance_test "C++" "$SRC_DIR/cpp/cpp_hello_world"
        if [ -f "$SRC_DIR/qt/build/QtHelloWorld" ]; then
            # Note: Qt GUI app needs special handling for performance tests
            echo "=== Qt CPU Performance ==="
            echo "Note: Qt application requires GUI environment for full testing"
            echo ""
        fi
        
    } | tee "$report_file"
    
    log "Report saved to: $report_file"
}

# Main function
main() {
    log "Starting Performance Measurement Script"
    
    # Setup
    check_tools || exit 1
    setup_results_dir
    
    # Build all applications
    build_applications || exit 1
    
    # Generate performance report
    generate_report
    
    log "Performance measurement complete!"
    info "Check the results in: $RESULTS_DIR"
}

# Script usage
usage() {
    cat << EOF
Usage: $0 [options]

Options:
    -h, --help      Show this help message
    -q, --quiet     Reduce output verbosity
    --no-build      Skip building applications
    --quick         Run with minimal iterations (faster but less accurate)

Examples:
    $0                  # Run full performance test
    $0 --quick          # Quick test with fewer iterations
    $0 --no-build       # Skip build step (use existing binaries)

EOF
}

# Parse command line arguments
QUIET=false
NO_BUILD=false
QUICK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -q|--quiet)
            QUIET=true
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

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
