// main_server.cpp
#include <QCoreApplication>
#include "server.h"
#include <QDBusConnection>
#include <QDBusError>
#include <QDebug>
#include <QTimer>

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    // Enable D-Bus debugging
    qputenv("QT_LOGGING_RULES", "qt.dbus.integration.debug=true");

    qDebug() << "Starting Qt D-Bus Server...";
    
    // Check if D-Bus session bus is available
    if (!QDBusConnection::sessionBus().isConnected()) {
        qCritical() << "Cannot connect to the D-Bus session bus.";
        qCritical() << "Please make sure D-Bus session is running.";
        qCritical() << "You can start it with: eval `dbus-launch --sh-syntax`";
        return 1;
    }

    Server server;
    
    // Register object on D-Bus
    if (!QDBusConnection::sessionBus().registerObject("/com/example/HelloWorld", &server, 
                                                      QDBusConnection::ExportAllSlots | 
                                                      QDBusConnection::ExportAllSignals)) {
        qCritical() << "Failed to register object on D-Bus!";
        qCritical() << "Error:" << QDBusConnection::sessionBus().lastError().message();
        return 1;
    }
    
    // Register service name on D-Bus
    if (!QDBusConnection::sessionBus().registerService("com.example.HelloWorldService")) {
        qCritical() << "Failed to register service on D-Bus!";
        qCritical() << "Error:" << QDBusConnection::sessionBus().lastError().message();
        return 1;
    }

    qDebug() << "Qt D-Bus Server started successfully!";
    qDebug() << "Service name: com.example.HelloWorldService";
    qDebug() << "Object path: /com/example/HelloWorld"; 
    qDebug() << "Interface: com.example.HelloWorld";
    qDebug() << "Waiting for client connections...";
    
    // Optional: Set up a timer for periodic status messages
    QTimer *statusTimer = new QTimer(&a);
    QObject::connect(statusTimer, &QTimer::timeout, [&]() {
        qDebug() << "Server is running at" << QDateTime::currentDateTime().toString();
    });
    statusTimer->start(30000); // Status message every 30 seconds

    return a.exec();
}
