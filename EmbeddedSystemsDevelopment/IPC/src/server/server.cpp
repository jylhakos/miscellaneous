// server.cpp
#include "server.h"
#include <QDebug>
#include <QDateTime>

Server::Server(QObject *parent) : QObject(parent)
{
    qDebug() << "Server object created at" << QDateTime::currentDateTime().toString();
}

QString Server::sayHello(const QString &name)
{
    qDebug() << "Server received request from:" << name;
    QString response = QString("Hello, %1 from Qt D-Bus Server!").arg(name);
    
    // Emit a signal to demonstrate signal broadcasting
    emit messageReceived(QString("Server processed request from: %1").arg(name));
    
    return response;
}

void Server::broadcastMessage(const QString &message)
{
    qDebug() << "Broadcasting message:" << message;
    emit messageReceived(message);
}
