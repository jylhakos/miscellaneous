#include <iostream>
#include <string>
#include <vector>

// Demonstrating C++ features with .c++ extension
class HelloWorld {
private:
    std::string message;
    std::vector<std::string> languages;

public:
    HelloWorld() : message("Hello, World!") {
        languages = {"English", "Spanish", "French", "German"};
    }

    void greet() const {
        std::cout << message << std::endl;
    }

    void greetInLanguages() const {
        std::vector<std::string> greetings = {
            "Hello, World!",      // English
            "¡Hola, Mundo!",      // Spanish
            "Bonjour, Monde!",    // French
            "Hallo, Welt!"        // German
        };

        for (size_t i = 0; i < languages.size() && i < greetings.size(); ++i) {
            std::cout << languages[i] << ": " << greetings[i] << std::endl;
        }
    }

    // C++11 auto keyword demonstration
    auto getMessageLength() const -> int {
        return static_cast<int>(message.length());
    }
};

int main() {
    std::cout << "=== C++ Demo with .c++ extension ===" << std::endl;
    
    HelloWorld hello;
    
    // Basic greeting
    hello.greet();
    std::cout << std::endl;
    
    // Multi-language greetings
    std::cout << "Greetings in different languages:" << std::endl;
    hello.greetInLanguages();
    std::cout << std::endl;
    
    // Modern C++ features demonstration
    std::cout << "Message length: " << hello.getMessageLength() << " characters" << std::endl;
    
    // Range-based for loop (C++11)
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    std::cout << "Numbers: ";
    for (const auto& num : numbers) {
        std::cout << num << " ";
    }
    std::cout << std::endl;
    
    std::cout << "=== Demo complete! ===" << std::endl;
    
    return 0;
}
