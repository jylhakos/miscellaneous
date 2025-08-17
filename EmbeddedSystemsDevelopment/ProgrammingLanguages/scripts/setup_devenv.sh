#!/bin/bash

# Development Environment Setup: Installs required tools for Qt, C++, and C development with RTOS support

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[SETUP]${NC} $1"
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

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        error "Cannot detect OS version"
        exit 1
    fi
    
    log "Detected OS: $OS $VER"
}

# Install basic development tools
install_basic_tools() {
    log "Installing basic development tools..."
    
    case $OS in
        ubuntu|debian)
            sudo apt-get update
            sudo apt-get install -y \
                build-essential \
                gcc \
                g++ \
                make \
                cmake \
                git \
                wget \
                curl \
                pkg-config \
                libc6-dev \
                linux-libc-dev
            ;;
        centos|rhel|fedora)
            if command -v dnf >/dev/null 2>&1; then
                sudo dnf groupinstall -y "Development Tools"
                sudo dnf install -y gcc gcc-c++ make cmake git wget curl pkgconfig
            else
                sudo yum groupinstall -y "Development Tools"
                sudo yum install -y gcc gcc-c++ make cmake git wget curl pkgconfig
            fi
            ;;
        *)
            warning "Unsupported OS: $OS"
            warning "Please install development tools manually"
            ;;
    esac
}

# Install Qt development environment
install_qt() {
    log "Installing Qt development environment..."
    
    case $OS in
        ubuntu|debian)
            sudo apt-get install -y \
                qt6-base-dev \
                qt6-tools-dev \
                qt6-tools-dev-tools \
                libqt6core6 \
                libqt6gui6 \
                libqt6widgets6 \
                qmake6
            ;;
        centos|rhel|fedora)
            if command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y qt6-qtbase-devel qt6-qttools-devel
            else
                sudo yum install -y qt6-qtbase-devel qt6-qttools-devel
            fi
            ;;
        *)
            warning "Qt packages may need manual installation for $OS"
            info "Consider downloading from: https://www.qt.io/download"
            ;;
    esac
    
    # Verify Qt installation
    if command -v qmake6 >/dev/null 2>&1 || command -v qt6-config >/dev/null 2>&1; then
        log "Qt installation successful"
    else
        warning "Qt installation may have failed"
    fi
}

# Install performance analysis tools
install_perf_tools() {
    log "Installing performance analysis tools..."
    
    case $OS in
        ubuntu|debian)
            sudo apt-get install -y \
                valgrind \
                perf \
                linux-tools-generic \
                gprof \
                cppcheck \
                htop \
                time \
                bc \
                strace \
                ltrace
            
            # Try to install additional performance tools
            sudo apt-get install -y \
                linux-perf \
                trace-cmd \
                kernelshark \
                || warning "Some performance tools not available"
            ;;
        centos|rhel|fedora)
            if command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y \
                    valgrind \
                    perf \
                    gprof \
                    cppcheck \
                    htop \
                    time \
                    bc \
                    strace \
                    ltrace
            else
                sudo yum install -y \
                    valgrind \
                    perf \
                    gprof \
                    cppcheck \
                    htop \
                    time \
                    bc \
                    strace \
                    ltrace
            fi
            ;;
        *)
            warning "Performance tools may need manual installation for $OS"
            ;;
    esac
}

# Install cross-compilation tools
install_cross_tools() {
    log "Installing cross-compilation tools..."
    
    case $OS in
        ubuntu|debian)
            sudo apt-get install -y \
                gcc-arm-linux-gnueabihf \
                g++-arm-linux-gnueabihf \
                gcc-aarch64-linux-gnu \
                g++-aarch64-linux-gnu
            
            # Try to install bare-metal ARM tools
            sudo apt-get install -y \
                gcc-arm-none-eabi \
                binutils-arm-none-eabi \
                || warning "ARM bare-metal tools not available in repositories"
            ;;
        centos|rhel|fedora)
            if command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y \
                    gcc-arm-linux-gnu \
                    gcc-c++-arm-linux-gnu \
                    gcc-aarch64-linux-gnu \
                    gcc-c++-aarch64-linux-gnu
            else
                sudo yum install -y \
                    gcc-arm-linux-gnu \
                    gcc-c++-arm-linux-gnu
            fi
            ;;
        *)
            warning "Cross-compilation tools may need manual installation for $OS"
            ;;
    esac
}

# Install additional development tools
install_additional_tools() {
    log "Installing additional development tools..."
    
    case $OS in
        ubuntu|debian)
            sudo apt-get install -y \
                gdb \
                gdb-multiarch \
                ddd \
                vim \
                emacs \
                code \
                clang \
                clang-tools \
                clang-format \
                doxygen \
                graphviz \
                || warning "Some additional tools not available"
            ;;
        centos|rhel|fedora)
            if command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y \
                    gdb \
                    vim \
                    emacs \
                    clang \
                    doxygen \
                    graphviz
            else
                sudo yum install -y \
                    gdb \
                    vim \
                    emacs \
                    clang \
                    doxygen \
                    graphviz
            fi
            ;;
        *)
            warning "Additional tools may need manual installation for $OS"
            ;;
    esac
}

# Setup environment variables
setup_environment() {
    log "Setting up environment variables..."
    
    local bashrc="$HOME/.bashrc"
    local profile="$HOME/.profile"
    
    # Add common environment variables
    cat >> "$bashrc" << 'EOF'

# Development environment setup
export PATH="$PATH:/usr/local/bin"
export MAKEFLAGS="-j$(nproc)"
export CC=gcc
export CXX=g++

# Qt environment
if [ -d "/usr/lib/qt6" ]; then
    export QT_DIR="/usr/lib/qt6"
    export PATH="$QT_DIR/bin:$PATH"
fi

# ARM cross-compilation
if command -v arm-linux-gnueabihf-gcc >/dev/null 2>&1; then
    export ARM_CC=arm-linux-gnueabihf-gcc
    export ARM_CXX=arm-linux-gnueabihf-g++
fi

EOF
    
    log "Environment variables added to $bashrc"
    info "Please run 'source ~/.bashrc' or restart your shell"
}

# Verify installation
verify_installation() {
    log "Verifying installation..."
    
    local missing=()
    
    # Check basic tools
    command -v gcc >/dev/null 2>&1 || missing+=("gcc")
    command -v g++ >/dev/null 2>&1 || missing+=("g++")
    command -v make >/dev/null 2>&1 || missing+=("make")
    command -v cmake >/dev/null 2>&1 || missing+=("cmake")
    
    # Check performance tools
    command -v valgrind >/dev/null 2>&1 || missing+=("valgrind")
    command -v perf >/dev/null 2>&1 || missing+=("perf")
    
    # Check Qt
    if ! command -v qmake6 >/dev/null 2>&1 && ! command -v qt6-config >/dev/null 2>&1; then
        missing+=("qt6")
    fi
    
    # Check cross-compilation
    if ! command -v arm-linux-gnueabihf-gcc >/dev/null 2>&1; then
        missing+=("arm-cross-gcc")
    fi
    
    if [ ${#missing[@]} -eq 0 ]; then
        log "All tools installed successfully!"
        
        # Show versions
        info "Tool versions:"
        printf "  GCC: %s\n" "$(gcc --version | head -1)"
        printf "  G++: %s\n" "$(g++ --version | head -1)"
        printf "  CMake: %s\n" "$(cmake --version | head -1)"
        
        if command -v qmake6 >/dev/null 2>&1; then
            printf "  Qt: %s\n" "$(qmake6 --version | grep Qt)"
        fi
        
        if command -v arm-linux-gnueabihf-gcc >/dev/null 2>&1; then
            printf "  ARM GCC: %s\n" "$(arm-linux-gnueabihf-gcc --version | head -1)"
        fi
        
    else
        warning "Some tools are missing: ${missing[*]}"
        return 1
    fi
}

# Main setup function
main() {
    log "Starting development environment setup..."
    
    detect_os
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        error "Please do not run this script as root"
        error "Use a regular user account with sudo access"
        exit 1
    fi
    
    # Check sudo access
    if ! sudo -n true 2>/dev/null; then
        log "This script requires sudo access for package installation"
        sudo -v
    fi
    
    install_basic_tools
    install_qt
    install_perf_tools
    install_cross_tools
    install_additional_tools
    setup_environment
    verify_installation
    
    log "Development environment setup complete!"
    info "You can now build the applications using the provided scripts"
    info "Run 'scripts/build_all.sh' to build all applications"
    info "Run 'scripts/measure_performance.sh' to benchmark performance"
}

# Show usage
usage() {
    cat << EOF
Usage: $0 [options]

Options:
    -h, --help      Show this help message
    --basic         Install only basic development tools
    --qt            Install only Qt development tools
    --perf          Install only performance analysis tools
    --cross         Install only cross-compilation tools
    --no-env        Skip environment setup

Examples:
    $0              # Full installation
    $0 --basic      # Install only basic tools
    $0 --qt --perf  # Install Qt and performance tools only

EOF
}

# Parse arguments
INSTALL_BASIC=true
INSTALL_QT=true
INSTALL_PERF=true
INSTALL_CROSS=true
INSTALL_ADDITIONAL=true
SETUP_ENV=true

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        --basic)
            INSTALL_BASIC=true
            INSTALL_QT=false
            INSTALL_PERF=false
            INSTALL_CROSS=false
            INSTALL_ADDITIONAL=false
            shift
            ;;
        --qt)
            if [ "$INSTALL_QT" = "false" ]; then
                INSTALL_QT=true
                INSTALL_BASIC=false
                INSTALL_PERF=false
                INSTALL_CROSS=false
                INSTALL_ADDITIONAL=false
            fi
            shift
            ;;
        --perf)
            if [ "$INSTALL_PERF" = "false" ]; then
                INSTALL_PERF=true
                INSTALL_BASIC=false
                INSTALL_QT=false
                INSTALL_CROSS=false
                INSTALL_ADDITIONAL=false
            fi
            shift
            ;;
        --cross)
            if [ "$INSTALL_CROSS" = "false" ]; then
                INSTALL_CROSS=true
                INSTALL_BASIC=false
                INSTALL_QT=false
                INSTALL_PERF=false
                INSTALL_ADDITIONAL=false
            fi
            shift
            ;;
        --no-env)
            SETUP_ENV=false
            shift
            ;;
        *)
            error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
