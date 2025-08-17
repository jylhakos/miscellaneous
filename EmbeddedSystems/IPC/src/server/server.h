// server.h
#ifndef SERVER_H
#define SERVER_H

#include <QObject>
#include <QDBusConnection>

class Server : public QObject
{
    Q_OBJECT
    Q_CLASSINFO("D-Bus Interface", "com.example.HelloWorld") // Define D-Bus interface name

public:
    explicit Server(QObject *parent = nullptr);

public slots:
    QString sayHello(const QString &name); // D-Bus callable method
    
signals:
    void messageReceived(const QString &message); // D-Bus signal

private slots:
    void broadcastMessage(const QString &message);
};

#endif // SERVER_H
