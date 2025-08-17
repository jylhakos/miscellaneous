CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2 -g
TARGET = cpp_hello_world
SOURCE = main.cpp

# Default target
all: $(TARGET)

# Build the main executable
$(TARGET): $(SOURCE)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCE)

# Debug build
debug: CXXFLAGS = -std=c++17 -Wall -Wextra -O0 -g -DDEBUG
debug: $(TARGET)

# Release build with maximum optimization
release: CXXFLAGS = -std=c++17 -Wall -Wextra -O3 -DNDEBUG -march=native
release: $(TARGET)

# Static build for deployment
static: CXXFLAGS = -std=c++17 -Wall -Wextra -O2 -static
static: $(TARGET)

# Cross-compilation for ARM
arm: CXX = arm-linux-gnueabihf-g++
arm: CXXFLAGS = -std=c++17 -Wall -Wextra -O2 -static
arm: TARGET = cpp_hello_world_arm
arm: $(TARGET)

# Performance profiling build
profile: CXXFLAGS = -std=c++17 -Wall -Wextra -O2 -g -pg
profile: $(TARGET)

# Run the application
run: $(TARGET)
	./$(TARGET)

# Run performance test
perf-test: $(TARGET)
	./$(TARGET) --perf

# Clean build artifacts
clean:
	rm -f $(TARGET) cpp_hello_world_arm gmon.out

# Install to system (requires sudo)
install: $(TARGET)
	install -d /usr/local/bin
	install -m 755 $(TARGET) /usr/local/bin/

# Create deployment package
deploy: release
	mkdir -p deploy
	cp $(TARGET) deploy/
	strip deploy/$(TARGET)
	echo "Deployment package created in deploy/"

.PHONY: all debug release static arm profile run perf-test clean install deploy
