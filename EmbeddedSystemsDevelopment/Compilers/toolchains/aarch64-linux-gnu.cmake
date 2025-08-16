# CMake toolchain file for ARM64/AArch64 cross-compilation
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

# Cross-compiler tools
set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)
set(CMAKE_ASM_COMPILER aarch64-linux-gnu-gcc)

# Linker and other tools
set(CMAKE_AR aarch64-linux-gnu-ar)
set(CMAKE_RANLIB aarch64-linux-gnu-ranlib)
set(CMAKE_STRIP aarch64-linux-gnu-strip)

# Sysroot (adjust path as needed)
# set(CMAKE_SYSROOT /usr/aarch64-linux-gnu)

# Compiler flags for ARM64
set(CMAKE_C_FLAGS_INIT "-march=armv8-a")
set(CMAKE_CXX_FLAGS_INIT "-march=armv8-a")

# Search paths
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

# Enable for Yocto SDK
if(DEFINED ENV{OECORE_TARGET_SYSROOT})
    set(CMAKE_SYSROOT $ENV{OECORE_TARGET_SYSROOT})
    set(CMAKE_FIND_ROOT_PATH $ENV{OECORE_TARGET_SYSROOT})
endif()

# Add target-specific definitions
add_definitions(-DTARGET_ARM64=1)
