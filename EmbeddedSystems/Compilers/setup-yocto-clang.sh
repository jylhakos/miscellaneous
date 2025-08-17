#!/bin/bash
# setup-yocto-clang.sh - Complete setup script for Yocto with Clang/LLVM support

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
YOCTO_DIR="${SCRIPT_DIR}/yocto-workspace"
POKY_VERSION="kirkstone"

echo "🚀 Yocto Project + Clang/LLVM Setup Script"
echo "==========================================="

# Check if running from correct directory
if [[ ! -f "${SCRIPT_DIR}/README.md" ]]; then
    echo "❌ Please run this script from the Compilers project root directory"
    exit 1
fi

# Install Yocto dependencies
echo "📦 Installing Yocto Project dependencies..."
sudo apt update
sudo apt install -y \\
    gawk wget git diffstat unzip texinfo gcc build-essential \\
    chrpath socat cpio python3 python3-pip python3-pexpect \\
    xz-utils debianutils iputils-ping python3-git python3-jinja2 \\
    libegl1-mesa libsdl1.2-dev python3-subunit mesa-common-dev \\
    zstd liblz4-tool file locales

# Set UTF-8 locale
sudo locale-gen en_US.UTF-8

# Create workspace if it doesn't exist
mkdir -p "${YOCTO_DIR}"
cd "${YOCTO_DIR}"

# Clone Poky if not already present
if [[ ! -d "poky" ]]; then
    echo "📥 Cloning Poky (Yocto reference distribution)..."
    git clone -b ${POKY_VERSION} https://git.yoctoproject.org/git/poky.git
else
    echo "  Poky already exists, updating..."
    cd poky
    git fetch origin
    git checkout ${POKY_VERSION}
    git pull
    cd ..
fi

# Clone meta-openembedded for additional packages
if [[ ! -d "meta-openembedded" ]]; then
    echo "📥 Cloning meta-openembedded..."
    git clone -b ${POKY_VERSION} https://git.openembedded.org/meta-openembedded
else
    echo "  meta-openembedded already exists, updating..."
    cd meta-openembedded
    git fetch origin
    git checkout ${POKY_VERSION}
    git pull
    cd ..
fi

# Clone meta-clang for advanced Clang/LLVM support
if [[ ! -d "meta-clang" ]]; then
    echo "⚡ Cloning meta-clang layer..."
    git clone -b ${POKY_VERSION} https://github.com/kraj/meta-clang.git
else
    echo "  meta-clang already exists, updating..."
    cd meta-clang
    git fetch origin
    git checkout ${POKY_VERSION}
    git pull
    cd ..
fi

# Update bblayers.conf to include meta-clang
echo "🔧 Updating bblayers.conf with meta-clang support..."
cat > build-demo/conf/bblayers.conf << 'EOF'
# POKY_BBLAYERS_CONF_VERSION is increased each time build/conf/bblayers.conf
# changes incompatibly
POKY_BBLAYERS_CONF_VERSION = "2"

BBPATH = "${TOPDIR}"
BBFILES ?= ""

BBLAYERS ?= " \\
  ${TOPDIR}/../poky/meta \\
  ${TOPDIR}/../poky/meta-poky \\
  ${TOPDIR}/../poky/meta-yocto-bsp \\
  ${TOPDIR}/../meta-openembedded/meta-oe \\
  ${TOPDIR}/../meta-openembedded/meta-python \\
  ${TOPDIR}/../meta-clang \\
  ${TOPDIR}/../meta-compilers-demo \\
  "
EOF

# Create enhanced local.conf with Clang support
echo "🔧 Creating enhanced local.conf with Clang/LLVM support..."
cat >> build-demo/conf/local.conf << 'EOF'

#
# Clang/LLVM Configuration Examples
#

# Example 1: Use Clang as system-wide compiler
# Uncomment the following lines to use Clang for all recipes:
# TOOLCHAIN = "clang"
# RUNTIME = "llvm"  # Use LLVM runtime (libc++, compiler-rt)

# Example 2: Mixed toolchain (GCC for system, Clang for specific recipes)
# Leave TOOLCHAIN as default "gcc" and use TOOLCHAIN = "clang" in specific recipes

# Example 3: Recipe-specific Clang configuration
# Add to individual .bb or .bbappend files:
# TOOLCHAIN = "clang"
# RUNTIME = "llvm"

#
# Clang-specific build variants
#

# Build our demos with different toolchain combinations
# Default GCC build
PREFERRED_PROVIDER_c99-demo = "c99-demo"
PREFERRED_PROVIDER_cpp17-demo = "cpp17-demo"

# Add Clang variants
IMAGE_INSTALL:append = " c99-demo-clang cpp17-demo-clang"

EOF

# Create Clang variant recipes
echo "🔨 Creating Clang variant recipes..."

# Create C99 Clang variant
mkdir -p meta-compilers-demo/recipes-examples/c99-demo-clang
cat > meta-compilers-demo/recipes-examples/c99-demo-clang/c99-demo-clang_1.0.bb << 'EOF'
require ../c99-demo/c99-demo_1.0.bb

SUMMARY = "C99 Compiler Features Demo (Clang)"
PN = "c99-demo-clang"

# Force Clang toolchain
TOOLCHAIN = "clang"

SRC_URI = "file://t.c"

do_install:append() {
    # Rename binary to avoid conflicts
    mv ${D}${bindir}/c99-demo ${D}${bindir}/c99-demo-clang
    rm -f ${D}${bindir}/c99-features
    ln -sf c99-demo-clang ${D}${bindir}/c99-features-clang
}

FILES:${PN} = "${bindir}/c99-demo-clang ${bindir}/c99-features-clang"
EOF

# Create symlink to source file
mkdir -p meta-compilers-demo/recipes-examples/c99-demo-clang/files
cd meta-compilers-demo/recipes-examples/c99-demo-clang/files
ln -sf ../../c99-demo/files/t.c .
cd - > /dev/null

# Create C++17 Clang variant
mkdir -p meta-compilers-demo/recipes-examples/cpp17-demo-clang
cat > meta-compilers-demo/recipes-examples/cpp17-demo-clang/cpp17-demo-clang_1.0.bb << 'EOF'
require ../cpp17-demo/cpp17-demo_1.0.bb

SUMMARY = "C++17 Compiler Features Demo (Clang + libc++)"
PN = "cpp17-demo-clang"

# Force Clang toolchain with LLVM runtime
TOOLCHAIN = "clang" 
RUNTIME = "llvm"

SRC_URI = "file://t.cpp"

do_install:append() {
    # Rename binary to avoid conflicts
    mv ${D}${bindir}/cpp17-demo ${D}${bindir}/cpp17-demo-clang
    rm -f ${D}${bindir}/cpp17-features
    ln -sf cpp17-demo-clang ${D}${bindir}/cpp17-features-clang
}

FILES:${PN} = "${bindir}/cpp17-demo-clang ${bindir}/cpp17-features-clang"
EOF

# Create symlink to source file
mkdir -p meta-compilers-demo/recipes-examples/cpp17-demo-clang/files
cd meta-compilers-demo/recipes-examples/cpp17-demo-clang/files
ln -sf ../../cpp17-demo/files/t.cpp .
cd - > /dev/null

# Create a comprehensive README for the Yocto setup
cat > README-YOCTO.md << 'EOF'
# Yocto Project with Clang/LLVM Integration

This directory contains a complete Yocto Project setup with advanced Clang/LLVM support.

## Quick Start

1. Run the setup script:
   ```bash
   ./setup-yocto-clang.sh
   ```

2. Initialize the build environment:
   ```bash
   cd yocto-workspace/poky
   source oe-init-build-env ../build-demo
   ```

3. Build the demo applications:
   ```bash
   # Build with GCC (default)
   bitbake c99-demo cpp17-demo
   
   # Build with Clang
   bitbake c99-demo-clang cpp17-demo-clang
   
   # Build complete image with all demos
   bitbake core-image-minimal
   ```

## Toolchain Configuration

### System-wide Clang (local.conf):
```bash
TOOLCHAIN = "clang"
RUNTIME = "llvm"  # Use libc++ instead of libstdc++
```

### Recipe-specific Clang (.bb file):
```bash
TOOLCHAIN = "clang"
RUNTIME = "gnu"   # Use with libstdc++ (default)
# or
RUNTIME = "llvm"  # Use with libc++
```

## Available Build Targets

- `c99-demo` - C99 features with GCC
- `c99-demo-clang` - C99 features with Clang
- `cpp17-demo` - C++17 features with GCC
- `cpp17-demo-clang` - C++17 features with Clang + libc++

## Testing

Run QEMU to test the built images:
```bash
runqemu qemux86-64 core-image-minimal
```

Inside QEMU:
```bash
c99-demo
cpp17-demo
c99-demo-clang
cpp17-demo-clang
```
EOF

echo "  Yocto Project with Clang/LLVM setup complete!"
echo ""
echo "Next steps:"
echo "1. cd ${YOCTO_DIR}/poky"
echo "2. source oe-init-build-env ../build-demo"
echo "3. bitbake c99-demo cpp17-demo"
echo ""
echo "For advanced Clang builds:"
echo "4. bitbake c99-demo-clang cpp17-demo-clang"
echo ""
echo "To build a complete image:"
echo "5. bitbake core-image-minimal"
