cmake_minimum_required(VERSION 3.16)
project(qt_ipc_server)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Core DBus)

qt6_standard_project_setup()

qt6_add_executable(qt_ipc_server
    server.h
    server.cpp
    main_server.cpp
)

target_link_libraries(qt_ipc_server Qt6::Core Qt6::DBus)

# Enable automoc for Q_OBJECT classes
set_target_properties(qt_ipc_server PROPERTIES
    AUTOMOC ON
)
