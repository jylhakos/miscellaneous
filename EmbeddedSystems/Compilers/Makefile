# Makefile for Embedded Compilers Project

# Compiler configuration
CC = gcc
CXX = g++
LD = ld

# Alternative compilers (can be overridden with make CC=clang)
# CC = clang
# CXX = clang++
# LD = lld

# Standards and flags
CFLAGS = -std=c99 -Wall -Wextra -Wpedantic
CXXFLAGS = -std=c++17 -Wall -Wextra -Wpedantic
LDFLAGS = 

# Build configurations
DEBUG_FLAGS = -g -O0 -DDEBUG
RELEASE_FLAGS = -O3 -DNDEBUG -s
SANITIZER_FLAGS = -fsanitize=address,undefined

# Directories
SRC_DIR = src
BUILD_DIR = build
CROSS_DIR = $(BUILD_DIR)/cross

# Source files
C_SRC = $(SRC_DIR)/C/t.c
CPP_SRC = $(SRC_DIR)/C++/t.cpp

# Targets
C_TARGET = $(BUILD_DIR)/hello_c
CPP_TARGET = $(BUILD_DIR)/hello_cpp

# Cross-compilation settings
CROSS_TARGET = aarch64-linux-gnu
CROSS_CC = clang --target=$(CROSS_TARGET) --sysroot=/usr/$(CROSS_TARGET)
CROSS_CXX = clang++ --target=$(CROSS_TARGET) --sysroot=/usr/$(CROSS_TARGET)

.PHONY: all clean debug release cross analyze help

# Default target
all: release

# Create directories
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(CROSS_DIR):
	@mkdir -p $(CROSS_DIR)

# Release builds
release: $(BUILD_DIR)
	$(CC) $(CFLAGS) $(RELEASE_FLAGS) $(C_SRC) -o $(C_TARGET)
	$(CXX) $(CXXFLAGS) $(RELEASE_FLAGS) $(CPP_SRC) -o $(CPP_TARGET)
	@echo "Release builds complete"

# Debug builds
debug: $(BUILD_DIR)
	$(CC) $(CFLAGS) $(DEBUG_FLAGS) $(C_SRC) -o $(C_TARGET)_debug
	$(CXX) $(CXXFLAGS) $(DEBUG_FLAGS) $(CPP_SRC) -o $(CPP_TARGET)_debug
	@echo "Debug builds complete"

# Debug builds with sanitizers
sanitize: $(BUILD_DIR)
	$(CC) $(CFLAGS) $(DEBUG_FLAGS) $(SANITIZER_FLAGS) $(C_SRC) -o $(C_TARGET)_sanitize
	$(CXX) $(CXXFLAGS) $(DEBUG_FLAGS) $(SANITIZER_FLAGS) $(CPP_SRC) -o $(CPP_TARGET)_sanitize
	@echo "Sanitizer builds complete"

# Cross-compilation
cross: $(CROSS_DIR)
	$(CROSS_CC) $(CFLAGS) $(RELEASE_FLAGS) $(C_SRC) -o $(CROSS_DIR)/hello_c_$(CROSS_TARGET)
	$(CROSS_CXX) $(CXXFLAGS) $(RELEASE_FLAGS) $(CPP_SRC) -o $(CROSS_DIR)/hello_cpp_$(CROSS_TARGET)
	@echo "Cross-compilation complete for $(CROSS_TARGET)"

# Generate LLVM IR
llvm-ir: $(BUILD_DIR)
	$(CC) -S -emit-llvm -O2 $(C_SRC) -o $(BUILD_DIR)/t.ll
	$(CXX) -S -emit-llvm -O2 $(CPP_SRC) -o $(BUILD_DIR)/t_cpp.ll
	@echo "LLVM IR files generated"

# Generate assembly
asm: $(BUILD_DIR)
	$(CC) -S -O2 $(C_SRC) -o $(BUILD_DIR)/t_clang.s
	gcc -S -O2 $(C_SRC) -o $(BUILD_DIR)/t_gcc.s
	@echo "Assembly files generated"

# Static analysis
analyze:
	@echo "Running static analysis..."
	@if command -v clang >/dev/null 2>&1; then \
		echo "Using Clang static analyzer:"; \
		clang --analyze -Xanalyzer -analyzer-output=text $(C_SRC); \
		clang++ --analyze -Xanalyzer -analyzer-output=text $(CPP_SRC); \
	else \
		echo "Using GCC static analysis:"; \
		$(CC) -fanalyzer -Wall -Wextra $(C_SRC) -fsyntax-only; \
		$(CXX) -Wall -Wextra $(CPP_SRC) -fsyntax-only; \
	fi
	@echo "Static analysis complete"

# Run tests
test: release
	@echo "Running C program:"
	./$(C_TARGET)
	@echo "Running C++ program:"
	./$(CPP_TARGET)

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR)
	@echo "Clean complete"

# Help target
help:
	@echo "Available targets:"
	@echo "  all      - Build release version (default)"
	@echo "  release  - Build optimized release version"
	@echo "  debug    - Build debug version with symbols"
	@echo "  sanitize - Build debug version with sanitizers"
	@echo "  cross    - Cross-compile for $(CROSS_TARGET)"
	@echo "  llvm-ir  - Generate LLVM intermediate representation"
	@echo "  asm      - Generate assembly files"
	@echo "  analyze  - Run static analysis"
	@echo "  test     - Build and run programs"
	@echo "  clean    - Remove build artifacts"
	@echo "  help     - Show this help message"
