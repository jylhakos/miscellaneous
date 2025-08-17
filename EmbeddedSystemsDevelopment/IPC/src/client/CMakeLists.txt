cmake_minimum_required(VERSION 3.16)
project(qt_ipc_client)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Core DBus)

qt6_standard_project_setup()

qt6_add_executable(qt_ipc_client
    main_client.cpp
)

target_link_libraries(qt_ipc_client Qt6::Core Qt6::DBus)

# Enable automoc for Q_OBJECT classes
set_target_properties(qt_ipc_client PROPERTIES
    AUTOMOC ON
)
