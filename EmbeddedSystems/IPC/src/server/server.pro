# Qt D-Bus Server
QT += core dbus
QT -= gui

CONFIG += c++17 console
CONFIG -= app_bundle

TARGET = qt_ipc_server

SOURCES += \
    server.cpp \
    main_server.cpp

HEADERS += \
    server.h

# Installation
target.path = $$[QT_INSTALL_EXAMPLES]/ipc/server
INSTALLS += target
