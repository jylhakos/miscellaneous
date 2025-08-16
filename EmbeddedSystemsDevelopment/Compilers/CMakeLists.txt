cmake_minimum_required(VERSION 3.20)
project(EmbeddedCompilers 
    VERSION 1.0 
    DESCRIPTION "C99 and C++17 Compiler Demonstrations for Embedded Systems" 
    LANGUAGES C CXX
)

# Set standards
set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Build type configuration
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose build type" FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "RelWithDebInfo" "MinSizeRel")
endif()

message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C Compiler: ${CMAKE_C_COMPILER_ID} ${CMAKE_C_COMPILER_VERSION}")
message(STATUS "C++ Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")

# Compiler options
set(COMMON_C_FLAGS "-Wall -Wextra -Wpedantic")
set(COMMON_CXX_FLAGS "-Wall -Wextra -Wpedantic")

if(CMAKE_C_COMPILER_ID MATCHES "Clang")
    message(STATUS "Using Clang compiler")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${COMMON_C_FLAGS} -Weverything -Wno-padded -Wno-unused-macros")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${COMMON_CXX_FLAGS} -Wno-padded -Wno-unused-macros")
    
    # Option for libc++
    option(USE_LIBCXX "Use libc++ instead of libstdc++" OFF)
    if(USE_LIBCXX)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")
        set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -stdlib=libc++ -lc++abi")
        message(STATUS "Using libc++ runtime library")
    endif()
elseif(CMAKE_C_COMPILER_ID MATCHES "GNU")
    message(STATUS "Using GCC compiler")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${COMMON_C_FLAGS} -Wformat=2 -Wcast-align -Wshadow")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${COMMON_CXX_FLAGS} -Weffc++ -Wold-style-cast")
endif()

# Cross-compilation support
if(CMAKE_CROSSCOMPILING)
    message(STATUS "Cross-compiling for ${CMAKE_SYSTEM_NAME} ${CMAKE_SYSTEM_PROCESSOR}")
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -march=armv8-a")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=armv8-a")
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "arm")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -march=armv7-a -mfpu=neon")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=armv7-a -mfpu=neon")
    endif()
endif()

# Options for different features
option(ENABLE_STATIC_ANALYSIS "Enable static analysis" OFF)
option(ENABLE_SANITIZERS "Enable runtime sanitizers" OFF)
option(GENERATE_LLVM_IR "Generate LLVM IR files" OFF)
option(BUILD_YOCTO_COMPATIBLE "Build with Yocto-compatible settings" OFF)

# Output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Main targets
add_executable(c99-demo src/C/t.c)
target_link_libraries(c99-demo PRIVATE m)

add_executable(cpp17-demo src/C++/t.cpp)
target_link_libraries(cpp17-demo PRIVATE pthread)

# Alternative C++ target if available
if(EXISTS "${CMAKE_SOURCE_DIR}/src/C++/t.c++")
    add_executable(cpp-alt src/C++/t.c++)
    target_link_libraries(cpp-alt PRIVATE pthread)
endif()

# Compiler-specific optimizations
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    target_compile_options(c99-demo PRIVATE -O3 -DNDEBUG)
    target_compile_options(cpp17-demo PRIVATE -O3 -DNDEBUG)
    if(TARGET cpp-alt)
        target_compile_options(cpp-alt PRIVATE -O3 -DNDEBUG)
    endif()
elseif(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_options(c99-demo PRIVATE -O0 -g)
    target_compile_options(cpp17-demo PRIVATE -O0 -g)
    if(TARGET cpp-alt)
        target_compile_options(cpp-alt PRIVATE -O0 -g)
    endif()
endif()

# Enable sanitizers for debug builds
if(ENABLE_SANITIZERS AND CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(SANITIZER_FLAGS "-fsanitize=address,undefined -fno-omit-frame-pointer")
    target_compile_options(c99-demo PRIVATE ${SANITIZER_FLAGS})
    target_link_options(c99-demo PRIVATE ${SANITIZER_FLAGS})
    target_compile_options(cpp17-demo PRIVATE ${SANITIZER_FLAGS})
    target_link_options(cpp17-demo PRIVATE ${SANITIZER_FLAGS})
    if(TARGET cpp-alt)
        target_compile_options(cpp-alt PRIVATE ${SANITIZER_FLAGS})
        target_link_options(cpp-alt PRIVATE ${SANITIZER_FLAGS})
    endif()
endif()

# Yocto-compatible builds
if(BUILD_YOCTO_COMPATIBLE)
    target_compile_definitions(c99-demo PRIVATE YOCTO_BUILD=1)
    target_compile_definitions(cpp17-demo PRIVATE YOCTO_BUILD=1)
    if(TARGET cpp-alt)
        target_compile_definitions(cpp-alt PRIVATE YOCTO_BUILD=1)
    endif()
endif()

# Generate LLVM IR (Clang only)
if(GENERATE_LLVM_IR AND CMAKE_C_COMPILER_ID MATCHES "Clang")
    add_custom_target(llvm_ir
        COMMAND ${CMAKE_C_COMPILER} -S -emit-llvm -O2 ${CMAKE_SOURCE_DIR}/src/C/t.c -o c99-demo.ll
        COMMAND ${CMAKE_CXX_COMPILER} -S -emit-llvm -O2 ${CMAKE_SOURCE_DIR}/src/C++/t.cpp -o cpp17-demo.ll
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        COMMENT "Generating LLVM IR files"
    )
endif()

# Custom targets for different compiler configurations
add_custom_target(gcc-build
    COMMAND ${CMAKE_COMMAND} -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -B${CMAKE_BINARY_DIR}/gcc ${CMAKE_SOURCE_DIR}
    COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR}/gcc --parallel
    COMMENT "Building with GCC"
)

if(CMAKE_CXX_COMPILER_ID MATCHES "Clang" OR COMMAND clang++)
    add_custom_target(clang-build
        COMMAND ${CMAKE_COMMAND} -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -B${CMAKE_BINARY_DIR}/clang ${CMAKE_SOURCE_DIR}
        COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR}/clang --parallel
        COMMENT "Building with Clang"
    )
    
    add_custom_target(clang-libcxx-build
        COMMAND ${CMAKE_COMMAND} -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DUSE_LIBCXX=ON -B${CMAKE_BINARY_DIR}/clang-libcxx ${CMAKE_SOURCE_DIR}
        COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR}/clang-libcxx --parallel
        COMMENT "Building with Clang and libc++"
    )
endif()

# Cross-compilation targets
add_custom_target(cross-arm64
    COMMAND ${CMAKE_COMMAND} -DCMAKE_TOOLCHAIN_FILE=${CMAKE_SOURCE_DIR}/toolchains/aarch64-linux-gnu.cmake -B${CMAKE_BINARY_DIR}/arm64 ${CMAKE_SOURCE_DIR}
    COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR}/arm64 --parallel
    COMMENT "Cross-compiling for ARM64"
)

add_custom_target(cross-armhf  
    COMMAND ${CMAKE_COMMAND} -DCMAKE_TOOLCHAIN_FILE=${CMAKE_SOURCE_DIR}/toolchains/arm-linux-gnueabihf.cmake -B${CMAKE_BINARY_DIR}/armhf ${CMAKE_SOURCE_DIR}
    COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR}/armhf --parallel
    COMMENT "Cross-compiling for ARM (hard float)"
)

# Installation
install(TARGETS c99-demo cpp17-demo
    RUNTIME DESTINATION bin
    COMPONENT applications
)

if(TARGET cpp-alt)
    install(TARGETS cpp-alt RUNTIME DESTINATION bin COMPONENT applications)
endif()

# Testing
enable_testing()
add_test(NAME c99_basic_test COMMAND c99-demo)
add_test(NAME cpp17_basic_test COMMAND cpp17-demo)
if(TARGET cpp-alt)
    add_test(NAME cpp_alt_test COMMAND cpp-alt)
endif()

# Performance tests (optional)
add_test(NAME c99_performance_test COMMAND ${CMAKE_COMMAND} -E time c99-demo)
add_test(NAME cpp17_performance_test COMMAND ${CMAKE_COMMAND} -E time cpp17-demo)

# Generate compile_commands.json for IDE support
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# CPack configuration for packaging
set(CPACK_PACKAGE_NAME "EmbeddedCompilers")
set(CPACK_PACKAGE_VERSION "${PROJECT_VERSION}")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "${PROJECT_DESCRIPTION}")
set(CPACK_PACKAGE_VENDOR "Embedded Systems Development")
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_SOURCE_DIR}/LICENSE")
include(CPack)

# Summary
message(STATUS "")
message(STATUS "=== Build Configuration Summary ===")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C Standard: C${CMAKE_C_STANDARD}")
message(STATUS "C++ Standard: C++${CMAKE_CXX_STANDARD}")
if(USE_LIBCXX)
    message(STATUS "C++ Runtime: libc++ (LLVM)")
else()
    message(STATUS "C++ Runtime: libstdc++ (GNU)")
endif()
message(STATUS "Sanitizers: ${ENABLE_SANITIZERS}")
message(STATUS "Static Analysis: ${ENABLE_STATIC_ANALYSIS}")
message(STATUS "LLVM IR Generation: ${GENERATE_LLVM_IR}")
message(STATUS "Cross Compiling: ${CMAKE_CROSSCOMPILING}")
if(CMAKE_CROSSCOMPILING)
    message(STATUS "Target System: ${CMAKE_SYSTEM_NAME}")
    message(STATUS "Target Processor: ${CMAKE_SYSTEM_PROCESSOR}")
endif()
message(STATUS "Install Prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "===================================")
message(STATUS "")
