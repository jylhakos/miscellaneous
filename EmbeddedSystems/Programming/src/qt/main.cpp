#include <QApplication>
#include <QWidget>
#include <QLabel>
#include <QVBoxLayout>
#include <QPushButton>
#include <QMessageBox>
#include <QTime>
#include <iostream>
#include <chrono>

class HelloWorldWidget : public QWidget
{
    Q_OBJECT

public:
    HelloWorldWidget(QWidget *parent = nullptr) : QWidget(parent)
    {
        setWindowTitle("Qt Hello World - RTOS Demo");
        setFixedSize(400, 300);
        
        // Create UI elements
        QVBoxLayout *layout = new QVBoxLayout(this);
        
        QLabel *titleLabel = new QLabel("Qt Hello World Application", this);
        titleLabel->setAlignment(Qt::AlignCenter);
        titleLabel->setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;");
        
        QLabel *infoLabel = new QLabel("Optimized for RTOS deployment", this);
        infoLabel->setAlignment(Qt::AlignCenter);
        infoLabel->setStyleSheet("font-size: 12px; color: gray;");
        
        QPushButton *helloButton = new QPushButton("Say Hello!", this);
        QPushButton *performanceButton = new QPushButton("Performance Test", this);
        QPushButton *exitButton = new QPushButton("Exit", this);
        
        // Add widgets to layout
        layout->addWidget(titleLabel);
        layout->addWidget(infoLabel);
        layout->addStretch();
        layout->addWidget(helloButton);
        layout->addWidget(performanceButton);
        layout->addWidget(exitButton);
        layout->addStretch();
        
        // Connect signals
        connect(helloButton, &QPushButton::clicked, this, &HelloWorldWidget::showHelloMessage);
        connect(performanceButton, &QPushButton::clicked, this, &HelloWorldWidget::runPerformanceTest);
        connect(exitButton, &QPushButton::clicked, this, &QWidget::close);
        
        // Record startup time
        startupTime = std::chrono::high_resolution_clock::now();
        std::cout << "Qt Application startup time recorded\n";
    }

private slots:
    void showHelloMessage()
    {
        auto now = std::chrono::high_resolution_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - startupTime).count();
        
        QString message = QString("Hello World from Qt!\n\nRunning for: %1 ms\nTimestamp: %2")
                         .arg(elapsed)
                         .arg(QTime::currentTime().toString());
        
        QMessageBox::information(this, "Qt Hello World", message);
        std::cout << "Hello World message displayed at " << elapsed << " ms\n";
    }
    
    void runPerformanceTest()
    {
        const int iterations = 1000000;
        auto start = std::chrono::high_resolution_clock::now();
        
        // Perform some computations
        volatile double result = 0.0;
        for (int i = 0; i < iterations; ++i) {
            result += i * 0.001;
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
        
        QString message = QString("Performance Test Results:\n\n"
                                "Iterations: %1\n"
                                "Time: %2 μs\n"
                                "Rate: %3 ops/sec\n"
                                "Result: %4")
                         .arg(iterations)
                         .arg(duration)
                         .arg(static_cast<long long>((iterations * 1000000.0) / duration))
                         .arg(result);
        
        QMessageBox::information(this, "Performance Test", message);
        std::cout << "Performance test completed: " << duration << " μs for " << iterations << " iterations\n";
    }

private:
    std::chrono::high_resolution_clock::time_point startupTime;
};

int main(int argc, char *argv[])
{
    std::cout << "Starting Qt Hello World Application...\n";
    
    QApplication app(argc, argv);
    
    HelloWorldWidget window;
    window.show();
    
    std::cout << "Qt Application initialized and displayed\n";
    
    return app.exec();
}

#include "main.moc"
