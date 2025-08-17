cmake_minimum_required(VERSION 3.16)
project(QtHelloWorld VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Qt6 components
find_package(Qt6 REQUIRED COMPONENTS Core Widgets)

# Enable Qt specific settings
qt_standard_project_setup()

# Create executable
qt_add_executable(QtHelloWorld main.cpp)

# Link Qt libraries
target_link_libraries(QtHelloWorld PRIVATE 
    Qt6::Core 
    Qt6::Widgets
)

# Compiler flags for optimization
if(CMAKE_BUILD_TYPE MATCHES Release)
    target_compile_options(QtHelloWorld PRIVATE -O3 -DNDEBUG)
endif()

# Installation rules
install(TARGETS QtHelloWorld
    BUNDLE  DESTINATION .
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

# Generate deployment script for Qt
qt_generate_deploy_app_script(
    TARGET QtHelloWorld
    OUTPUT_SCRIPT deploy_script
    NO_UNSUPPORTED_PLATFORM_ERROR
)

# Install deployment script
install(SCRIPT ${deploy_script})
