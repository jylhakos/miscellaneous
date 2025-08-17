/**
 * @file t.cpp
 * @brief Comprehensive C++17 features demonstration
 * @date 2025-08-16
 * 
 * This file demonstrates modern C++17 features including:
 * - Structured bindings
 * - std::optional
 * - std::string_view
 * - if constexpr
 * - fold expressions
 * - class template argument deduction
 * - constexpr if
 * - inline variables
 * - nested namespaces
 * - std::filesystem
 * - parallel STL algorithms
 */

#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <tuple>
#include <optional>
#include <variant>
#include <any>
#include <algorithm>
#include <numeric>
#include <memory>
#include <chrono>
#include <iomanip>
#include <filesystem>
#include <execution>

// C++17 nested namespace
namespace embedded::systems::demo {

    // C++17 inline variable
    inline constexpr int VERSION = 17;
    inline const std::string COMPILER_INFO = 
#ifdef __GNUC__
        "GCC " + std::string(__VERSION__);
#elif defined(__clang__)
        "Clang " + std::string(__clang_version__);
#else
        "Unknown compiler";
#endif

    // Template with C++17 fold expressions
    template<typename... Args>
    constexpr auto sum(Args... args) {
        return (args + ...);  // C++17 fold expression
    }

    template<typename... Args>
    constexpr auto multiply(Args... args) {
        return (args * ...);
    }

    template<typename... Args>
    void print_all(Args... args) {
        ((std::cout << args << " "), ...);  // C++17 fold expression
        std::cout << std::endl;
    }

    // Class demonstrating C++17 features
    class SystemInfo {
    private:
        std::string name_;
        int version_;
        std::optional<std::string> description_;
        std::vector<std::pair<std::string, int>> metrics_;

    public:
        // C++17 class template argument deduction will work with std::pair
        SystemInfo(std::string name, int version) 
            : name_(std::move(name)), version_(version) {
            metrics_.emplace_back("cpu_usage", 45);
            metrics_.emplace_back("memory_usage", 78);
            metrics_.emplace_back("disk_usage", 23);
        }

        void set_description(const std::string& desc) {
            description_ = desc;
        }

        // Using std::string_view for efficient string handling
        void process_data(std::string_view data) const {
            std::cout << "Processing data: " << data << std::endl;
            std::cout << "Data length: " << data.length() << " characters" << std::endl;
        }

        // C++17 structured bindings
        void display_metrics() const {
            std::cout << "\nSystem Metrics for " << name_ << " v" << version_ << ":\n";
            for (const auto& [metric_name, value] : metrics_) {
                std::cout << "  " << metric_name << ": " << value << "%" << std::endl;
            }
        }

        // Using std::optional
        void display_description() const {
            if (description_.has_value()) {
                std::cout << "Description: " << description_.value() << std::endl;
            } else {
                std::cout << "No description available" << std::endl;
            }
        }

        // Template with if constexpr
        template<typename T>
        void process_value(const T& value) const {
            if constexpr (std::is_arithmetic_v<T>) {
                std::cout << "Processing arithmetic value: " << value << std::endl;
                if constexpr (std::is_integral_v<T>) {
                    std::cout << "  -> Integer type with value: " << value << std::endl;
                } else {
                    std::cout << "  -> Floating-point type with value: " << value << std::endl;
                }
            } else if constexpr (std::is_same_v<T, std::string>) {
                std::cout << "Processing string value: \"" << value << "\"" << std::endl;
            } else {
                std::cout << "Processing other type" << std::endl;
            }
        }

        const std::vector<std::pair<std::string, int>>& get_metrics() const {
            return metrics_;
        }
    };

    // Function demonstrating std::variant
    void demonstrate_variant() {
        std::cout << "\n=== std::variant Demonstration ===\n";
        
        std::variant<int, double, std::string> value;
        
        value = 42;
        std::visit([](const auto& v) {
            std::cout << "Variant holds: " << v << " (type: " << typeid(v).name() << ")\n";
        }, value);
        
        value = 3.14159;
        std::visit([](const auto& v) {
            std::cout << "Variant holds: " << v << " (type: " << typeid(v).name() << ")\n";
        }, value);
        
        value = std::string("Hello, C++17!");
        std::visit([](const auto& v) {
            std::cout << "Variant holds: " << v << " (type: " << typeid(v).name() << ")\n";
        }, value);
    }

    // Function demonstrating std::any
    void demonstrate_any() {
        std::cout << "\n=== std::any Demonstration ===\n";
        
        std::any anything;
        
        anything = 100;
        if (anything.has_value()) {
            std::cout << "any contains: " << std::any_cast<int>(anything) << std::endl;
        }
        
        anything = std::string("C++17 is great!");
        try {
            auto str = std::any_cast<std::string>(anything);
            std::cout << "any contains: " << str << std::endl;
        } catch (const std::bad_any_cast& e) {
            std::cout << "Bad any_cast: " << e.what() << std::endl;
        }
    }

    // Function using C++17 algorithms with execution policies
    void demonstrate_parallel_algorithms() {
        std::cout << "\n=== Parallel Algorithms Demonstration ===\n";
        
        std::vector<int> data(1000000);
        std::iota(data.begin(), data.end(), 1);  // Fill with 1, 2, 3, ..., 1000000
        
        // Sequential execution
        auto start = std::chrono::high_resolution_clock::now();
        auto result_seq = std::accumulate(data.begin(), data.end(), 0LL);
        auto end = std::chrono::high_resolution_clock::now();
        auto duration_seq = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "Sequential sum of 1..1000000: " << result_seq << std::endl;
        std::cout << "Sequential time: " << duration_seq.count() << " microseconds" << std::endl;
        
        // Try parallel execution (if supported)
        try {
            start = std::chrono::high_resolution_clock::now();
            auto result_par = std::reduce(std::execution::par, data.begin(), data.end(), 0LL);
            end = std::chrono::high_resolution_clock::now();
            auto duration_par = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            
            std::cout << "Parallel sum of 1..1000000: " << result_par << std::endl;
            std::cout << "Parallel time: " << duration_par.count() << " microseconds" << std::endl;
        } catch (...) {
            std::cout << "Parallel execution not supported on this system" << std::endl;
        }
    }

    // Function demonstrating std::filesystem (if available)
    void demonstrate_filesystem() {
        std::cout << "\n=== std::filesystem Demonstration ===\n";
        
        try {
            namespace fs = std::filesystem;
            
            fs::path current_path = fs::current_path();
            std::cout << "Current directory: " << current_path << std::endl;
            std::cout << "Parent directory: " << current_path.parent_path() << std::endl;
            std::cout << "Filename: " << current_path.filename() << std::endl;
            
            // Check if the current directory exists (it should)
            if (fs::exists(current_path)) {
                std::cout << "Current directory exists and is ";
                if (fs::is_directory(current_path)) {
                    std::cout << "a directory" << std::endl;
                }
            }
            
            // Get file information
            auto space_info = fs::space(current_path);
            std::cout << "Disk space - Available: " 
                      << (space_info.available >> 20) << " MB" << std::endl;
                      
        } catch (const std::filesystem::filesystem_error& e) {
            std::cout << "Filesystem error: " << e.what() << std::endl;
        }
    }

} // namespace embedded::systems::demo

int main() {
    using namespace embedded::systems::demo;
    
    std::cout << "===== Comprehensive C++17 Features Demonstration =====\n";
    std::cout << "Compiler: " << COMPILER_INFO << std::endl;
    std::cout << "C++ Standard: " << __cplusplus << std::endl;
    std::cout << "Demo Version: " << VERSION << std::endl;

    // Demonstrate fold expressions
    std::cout << "\n=== Fold Expressions ===\n";
    std::cout << "Sum of 1,2,3,4,5: " << sum(1, 2, 3, 4, 5) << std::endl;
    std::cout << "Product of 2,3,4: " << multiply(2, 3, 4) << std::endl;
    std::cout << "Print all: ";
    print_all("Hello", 42, 3.14, "World!");

    // Demonstrate SystemInfo class
    std::cout << "\n=== SystemInfo Class Demo ===\n";
    SystemInfo system("EmbeddedOS", 17);
    system.set_description("Advanced embedded operating system with C++17 support");
    
    system.display_description();
    system.display_metrics();
    
    // Using std::string_view
    system.process_data("Sample sensor data from embedded device");
    
    // Template with if constexpr
    std::cout << "\n=== Constexpr If Template ===\n";
    system.process_value(42);
    system.process_value(3.14159);
    system.process_value(std::string("C++17"));

    // C++17 structured bindings with map
    std::cout << "\n=== Structured Bindings ===\n";
    std::map<std::string, int> device_status = {
        {"temperature", 75},
        {"humidity", 60},
        {"pressure", 1013}
    };
    
    for (const auto& [sensor, reading] : device_status) {
        std::cout << sensor << ": " << reading;
        if (sensor == "temperature") std::cout << "°C";
        else if (sensor == "humidity") std::cout << "%";
        else if (sensor == "pressure") std::cout << " hPa";
        std::cout << std::endl;
    }

    // C++17 tuple structured bindings
    auto get_coordinates = []() -> std::tuple<double, double, double> {
        return {45.7749, -122.4194, 56.7};  // Latitude, Longitude, Elevation
    };
    
    auto [latitude, longitude, elevation] = get_coordinates();
    std::cout << "\nGPS Coordinates:\n";
    std::cout << "Latitude: " << std::setprecision(4) << latitude << "°\n";
    std::cout << "Longitude: " << std::setprecision(4) << longitude << "°\n";
    std::cout << "Elevation: " << elevation << "m\n";

    // C++17 Class Template Argument Deduction (CTAD)
    std::cout << "\n=== Class Template Argument Deduction ===\n";
    std::pair device_info{"SensorNode", 42};  // Deduced as std::pair<const char*, int>
    std::vector readings{1.2, 3.4, 5.6, 7.8};  // Deduced as std::vector<double>
    
    std::cout << "Device: " << device_info.first << ", ID: " << device_info.second << std::endl;
    std::cout << "Readings: ";
    for (const auto& reading : readings) {
        std::cout << reading << " ";
    }
    std::cout << std::endl;

    // Optional demonstration
    std::cout << "\n=== std::optional Demonstration ===\n";
    auto find_sensor = [](const std::string& name) -> std::optional<int> {
        static std::map<std::string, int> sensors = {
            {"temp", 23}, {"humidity", 65}, {"pressure", 1013}
        };
        auto it = sensors.find(name);
        return (it != sensors.end()) ? std::optional{it->second} : std::nullopt;
    };
    
    if (auto value = find_sensor("temp"); value.has_value()) {
        std::cout << "Temperature sensor value: " << *value << std::endl;
    }
    
    if (auto value = find_sensor("nonexistent"); !value.has_value()) {
        std::cout << "Sensor 'nonexistent' not found" << std::endl;
    }

    // Demonstrate other C++17 features
    demonstrate_variant();
    demonstrate_any();
    demonstrate_parallel_algorithms();
    demonstrate_filesystem();

    std::cout << "\n===== End of C++17 Demonstration =====\n";
    return 0;
}