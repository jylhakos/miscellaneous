#include <iostream>
#include <chrono>
#include <thread>
#include <vector>
#include <memory>
#include <string>
#include <iomanip>
#include <cmath>

class PerformanceTimer {
private:
    std::chrono::high_resolution_clock::time_point start_time;
    std::chrono::high_resolution_clock::time_point end_time;
    
public:
    void start() {
        start_time = std::chrono::high_resolution_clock::now();
    }
    
    void stop() {
        end_time = std::chrono::high_resolution_clock::now();
    }
    
    double getDurationMicroseconds() const {
        return std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();
    }
    
    double getDurationMilliseconds() const {
        return std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();
    }
};

class HelloWorldApp {
private:
    std::chrono::high_resolution_clock::time_point app_start_time;
    
public:
    HelloWorldApp() : app_start_time(std::chrono::high_resolution_clock::now()) {
        std::cout << "C++ Hello World Application initialized\n";
        std::cout << "Optimized for RTOS deployment\n";
        std::cout << "Build timestamp: " << __DATE__ << " " << __TIME__ << "\n";
        std::cout << "----------------------------------------\n\n";
    }
    
    void displayHello() {
        auto now = std::chrono::high_resolution_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - app_start_time).count();
        
        std::cout << "Hello World from C++!\n";
        std::cout << "Runtime: " << elapsed << " ms\n";
        std::cout << "Thread ID: " << std::this_thread::get_id() << "\n\n";
    }
    
    void runPerformanceTest() {
        std::cout << "Starting C++ Performance Test...\n";
        
        const int iterations = 1000000;
        PerformanceTimer timer;
        
        // Test 1: Integer operations
        timer.start();
        volatile long long int_result = 0;
        for (int i = 0; i < iterations; ++i) {
            int_result += i * 2;
        }
        timer.stop();
        
        std::cout << "Integer Operations:\n";
        std::cout << "  Iterations: " << iterations << "\n";
        std::cout << "  Time: " << std::fixed << std::setprecision(2) << timer.getDurationMicroseconds() << " μs\n";
        std::cout << "  Rate: " << std::fixed << std::setprecision(0) << (iterations / (timer.getDurationMicroseconds() / 1000000.0)) << " ops/sec\n";
        std::cout << "  Result: " << int_result << "\n\n";
        
        // Test 2: Floating-point operations
        timer.start();
        volatile double float_result = 0.0;
        for (int i = 0; i < iterations; ++i) {
            float_result += std::sin(i * 0.001) * std::cos(i * 0.001);
        }
        timer.stop();
        
        std::cout << "Floating-Point Operations (sin/cos):\n";
        std::cout << "  Iterations: " << iterations << "\n";
        std::cout << "  Time: " << std::fixed << std::setprecision(2) << timer.getDurationMicroseconds() << " μs\n";
        std::cout << "  Rate: " << std::fixed << std::setprecision(0) << (iterations / (timer.getDurationMicroseconds() / 1000000.0)) << " ops/sec\n";
        std::cout << "  Result: " << std::fixed << std::setprecision(6) << float_result << "\n\n";
        
        // Test 3: Memory operations
        timer.start();
        std::vector<int> memory_test(iterations / 1000);
        for (size_t i = 0; i < memory_test.size(); ++i) {
            memory_test[i] = i * i;
        }
        timer.stop();
        
        std::cout << "Memory Operations (vector allocation/access):\n";
        std::cout << "  Elements: " << memory_test.size() << "\n";
        std::cout << "  Time: " << std::fixed << std::setprecision(2) << timer.getDurationMicroseconds() << " μs\n";
        std::cout << "  Rate: " << std::fixed << std::setprecision(0) << (memory_test.size() / (timer.getDurationMicroseconds() / 1000000.0)) << " ops/sec\n\n";
    }
    
    void displaySystemInfo() {
        std::cout << "System Information:\n";
        std::cout << "  C++ Standard: " << __cplusplus << "\n";
        std::cout << "  Compiler: " << 
#ifdef __GNUC__
            "GCC " << __GNUC__ << "." << __GNUC_MINOR__ << "." << __GNUC_PATCHLEVEL__ <<
#elif defined(__clang__)
            "Clang " << __clang_major__ << "." << __clang_minor__ << "." << __clang_patchlevel__ <<
#elif defined(_MSC_VER)
            "MSVC " << _MSC_VER <<
#else
            "Unknown" <<
#endif
            "\n";
        std::cout << "  Hardware threads: " << std::thread::hardware_concurrency() << "\n";
        std::cout << "  Pointer size: " << sizeof(void*) * 8 << " bits\n\n";
    }
    
    void runInteractiveMenu() {
        std::string input;
        
        while (true) {
            std::cout << "C++ Hello World Menu:\n";
            std::cout << "1. Display Hello Message\n";
            std::cout << "2. Run Performance Test\n";
            std::cout << "3. Display System Info\n";
            std::cout << "4. Exit\n";
            std::cout << "Enter choice (1-4): ";
            
            std::getline(std::cin, input);
            
            if (input == "1") {
                displayHello();
            } else if (input == "2") {
                runPerformanceTest();
            } else if (input == "3") {
                displaySystemInfo();
            } else if (input == "4") {
                std::cout << "Goodbye!\n";
                break;
            } else {
                std::cout << "Invalid choice. Please try again.\n\n";
            }
        }
    }
};

int main(int argc, char* argv[]) {
    std::cout << "Starting C++ Hello World Application...\n";
    std::cout << "Arguments: " << argc << "\n";
    
    for (int i = 0; i < argc; ++i) {
        std::cout << "  argv[" << i << "]: " << argv[i] << "\n";
    }
    std::cout << "\n";
    
    // Check for command-line arguments
    if (argc > 1) {
        std::string arg = argv[1];
        if (arg == "--hello") {
            HelloWorldApp app;
            app.displayHello();
            return 0;
        } else if (arg == "--perf") {
            HelloWorldApp app;
            app.runPerformanceTest();
            return 0;
        } else if (arg == "--info") {
            HelloWorldApp app;
            app.displaySystemInfo();
            return 0;
        } else if (arg == "--help") {
            std::cout << "Usage: " << argv[0] << " [options]\n";
            std::cout << "Options:\n";
            std::cout << "  --hello    Display hello message and exit\n";
            std::cout << "  --perf     Run performance test and exit\n";
            std::cout << "  --info     Display system information and exit\n";
            std::cout << "  --help     Display this help message\n";
            std::cout << "  (no args)  Run interactive menu\n";
            return 0;
        }
    }
    
    // Run interactive menu by default
    HelloWorldApp app;
    app.runInteractiveMenu();
    
    return 0;
}
