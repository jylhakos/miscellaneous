// main_client.cpp
#include <QCoreApplication>
#include <QDBusInterface>
#include <QDBusReply>
#include <QDBusError>
#include <QDebug>
#include <QDateTime>
#include <QTimer>

class Client : public QObject
{
    Q_OBJECT

public:
    Client(QObject *parent = nullptr) : QObject(parent) {}

public slots:
    void connectToServer() {
        // Create D-Bus interface
        interface = new QDBusInterface("com.example.HelloWorldService", // Service name
                                       "/com/example/HelloWorld",        // Object path
                                       "com.example.HelloWorld",         // Interface name
                                       QDBusConnection::sessionBus(), this);

        if (!interface->isValid()) {
            qCritical() << "D-Bus interface not valid:" << interface->lastError().message();
            qCritical() << "Make sure the server is running!";
            QCoreApplication::exit(1);
            return;
        }

        qDebug() << "Connected to D-Bus service successfully!";
        
        // Connect to server signals (if any)
        connect(interface, SIGNAL(messageReceived(QString)), 
                this, SLOT(onMessageReceived(QString)));

        // Make the IPC call
        makeIpcCall();
    }

    void makeIpcCall() {
        qDebug() << "Making D-Bus call to server...";
        
        // Synchronous call
        QDBusReply<QString> reply = interface->call("sayHello", "Qt Client");

        if (reply.isValid()) {
            qDebug() << "Client received response:" << reply.value();
        } else {
            qCritical() << "D-Bus call failed:" << reply.error().message();
            
            // Detailed error information
            QDBusError error = reply.error();
            switch (error.type()) {
                case QDBusError::ServiceUnknown:
                    qCritical() << "Service not available - is the server running?";
                    break;
                case QDBusError::Timeout:
                    qCritical() << "Call timed out";
                    break;
                case QDBusError::AccessDenied:
                    qCritical() << "Access denied";
                    break;
                default:
                    qCritical() << "Other D-Bus error:" << error.name();
            }
            
            QCoreApplication::exit(1);
            return;
        }

        // Demonstrate asynchronous call
        qDebug() << "Making asynchronous D-Bus call...";
        QDBusPendingCall async = interface->asyncCall("sayHello", "Async Qt Client");
        QDBusPendingCallWatcher *watcher = new QDBusPendingCallWatcher(async, this);
        connect(watcher, &QDBusPendingCallWatcher::finished, this, &Client::handleAsyncReply);
    }

private slots:
    void onMessageReceived(const QString &message) {
        qDebug() << "Received D-Bus signal:" << message;
    }

    void handleAsyncReply(QDBusPendingCallWatcher *call) {
        QDBusPendingReply<QString> reply = *call;
        if (reply.isError()) {
            qCritical() << "Async call failed:" << reply.error().message();
        } else {
            qDebug() << "Async call response:" << reply.argumentAt<0>();
        }
        call->deleteLater();
        
        // Exit after demonstrations
        QTimer::singleShot(1000, QCoreApplication::instance(), &QCoreApplication::quit);
    }

private:
    QDBusInterface *interface = nullptr;
};

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    // Enable D-Bus debugging
    qputenv("QT_LOGGING_RULES", "qt.dbus.integration.debug=true");

    qDebug() << "Starting Qt D-Bus Client at" << QDateTime::currentDateTime().toString();
    
    // Check if D-Bus session bus is available
    if (!QDBusConnection::sessionBus().isConnected()) {
        qCritical() << "Cannot connect to the D-Bus session bus.";
        qCritical() << "Please make sure D-Bus session is running.";
        return 1;
    }

    Client client;
    
    // Connect to server after a short delay to ensure server is ready
    QTimer::singleShot(500, &client, &Client::connectToServer);

    return a.exec();
}

#include "main_client.moc"
