# CMake toolchain file for ARM (32-bit) cross-compilation with hard float
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR arm)

# Cross-compiler tools
set(CMAKE_C_COMPILER arm-linux-gnueabihf-gcc)
set(CMAKE_CXX_COMPILER arm-linux-gnueabihf-g++)
set(CMAKE_ASM_COMPILER arm-linux-gnueabihf-gcc)

# Linker and other tools  
set(CMAKE_AR arm-linux-gnueabihf-ar)
set(CMAKE_RANLIB arm-linux-gnueabihf-ranlib)
set(CMAKE_STRIP arm-linux-gnueabihf-strip)

# Sysroot (adjust path as needed)
# set(CMAKE_SYSROOT /usr/arm-linux-gnueabihf)

# Compiler flags for ARM with hard float and NEON
set(CMAKE_C_FLAGS_INIT "-march=armv7-a -mfpu=neon -mfloat-abi=hard")
set(CMAKE_CXX_FLAGS_INIT "-march=armv7-a -mfpu=neon -mfloat-abi=hard")

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
add_definitions(-DTARGET_ARM=1 -DTARGET_ARM_HARDFP=1)
