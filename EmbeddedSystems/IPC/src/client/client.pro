# Qt D-Bus Client
QT += core dbus
QT -= gui

CONFIG += c++17 console
CONFIG -= app_bundle

TARGET = qt_ipc_client

SOURCES += \
    main_client.cpp

# Installation
target.path = $$[QT_INSTALL_EXAMPLES]/ipc/client
INSTALLS += target
