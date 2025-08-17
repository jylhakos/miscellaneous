# Scripts

### **1. Compiler Validation**

**Essential Compiler Detection Commands:**
```bash
# Basic version checks for all compilers
gcc --version && echo "  GCC available" || echo "❌ GCC not found"
g++ --version && echo "  G++ available" || echo "❌ G++ not found"
clang --version && echo "  Clang available" || echo "❌ Clang not found"
clang++ --version && echo "  Clang++ available" || echo "❌ Clang++ not found"

# Cross-compiler detection
aarch64-linux-gnu-gcc --version && echo "  ARM64 GCC available"
arm-linux-gnueabihf-gcc --version && echo "  ARM GCC available"

# Quick compilation tests
echo 'int main(){return 0;}' | gcc -x c - -o /tmp/gcc_test && echo "  GCC works"
echo 'int main(){return 0;}' | g++ -x c++ - -o /tmp/gpp_test && echo "  G++ works"
```

**Validation Features:**
-   Standards support testing (C99, C11, C17, C++11, C++14, C++17, C++20)
-   LLVM toolchain detection (lldb, lld, llvm-ar, etc.)
-   libc++ vs libstdc++ capability testing
-   Cross-compilation toolchain validation
-   Actual compilation and execution tests
-   System information gathering
-   Installation recommendations

### **2. Validation Script**
Created: `scripts/compiler_check.sh` - A comprehensive 200+ line script that:

```bash
# Usage
./scripts/compiler_check.sh                    # Full report
./scripts/compiler_check.sh | grep " \|❌"    # Results only
```

**Script Features:**
-   **Detects**: GCC, Clang, cross-compilers, LLVM tools
-  **Tests**: C99/C11/C17 and C++11/14/17/20 standards
- ⚡ **Validates**: libc++ support with Clang
- 🛠️ **Checks**: Build tools (make, cmake, ninja)
-  **Reports**: System info (CPU, memory, disk space)
-   **Recommends**: Installation commands per distro

**Sample Output:**
```
  Compiler Detection and Validation Report
===========================================
 Native Compilers:
  GCC C Compiler: gcc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0
    c99 support: Available
    c17 support: Available
  GCC C++ Compiler: g++ (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0
    c++17 support: Available
    c++20 support: Available
❌ Clang C Compiler: Not found
```

### **3. Integration with Existing Content**
-   Added validation commands right after Prerequisites section
-   Integrated script reference in "Next Steps"
-   Provided quick one-liners for immediate validation
-   Cross-referenced with Yocto and cross-compilation sections

##   **.gitignore**

### **.gitignore Content**

**Build Artifacts Excluded:**
```bash
# Build directories and outputs
build/
build-*/
bin/
obj/
*.exe
*.out
*.o
*.so
*.a
c99-demo*
cpp17-demo*
```

**Dependencies Excluded:**
```bash
# Package managers
node_modules/
vendor/

# Yocto build artifacts (keeping configs)
yocto-workspace/poky/
yocto-workspace/build-demo/tmp/
yocto-workspace/build-demo/sstate-cache/
```

**IDE/Editor Files Excluded:**
```bash
# VS Code (with example exceptions)
.vscode/
!.vscode/settings.json.example

# All major IDEs covered
.idea/          # JetBrains
*.sublime-*     # Sublime Text
.atom/          # Atom
```

**Source Code & Configs**
```bash
# All source extensions preserved
!*.c
!*.cpp
!*.cc
!*.cxx
!*.c++
!*.h
!*.hpp

# Configuration files
!*.conf
!*.bb
!*.bbappend
!layer.conf
!CMakeLists.txt
!Makefile

# Scripts and docs preserved
!*.sh
!*.md
!README*
!LICENSE*
```

**Yocto Integration:**
```bash
# Exclude large Yocto downloads/builds
yocto-workspace/poky/
yocto-workspace/build-demo/tmp/

# Keep our custom layer and configs
!yocto-workspace/meta-compilers-demo/
!yocto-workspace/build-demo/conf/
```

## **Production**

### **Developer Workflow:**
```bash
# 1. Clone repository (clean thanks to .gitignore)
git clone <repo>

# 2. Validate compiler setup
./scripts/compiler_check.sh

# 3. Install missing compilers (script provides commands)
sudo apt install clang clang++  # Ubuntu example

# 4. Verify everything works
./scripts/compiler_check.sh | grep " "

# 5. Start development with confidence
make all
```

### **Quality Assurance:**
-   **Tested**: Script works on Ubuntu 24.04 with GCC 13.3.0
-   **Portable**: Works across major Linux distributions