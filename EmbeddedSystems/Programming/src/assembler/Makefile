# Assembly (x86) Makefile for Hello World Program
# Supports multiple build configurations and cross-platform development

# Assembler and linker settings
ASM = nasm
LD = ld
OBJDUMP = objdump
HEXDUMP = hexdump

# Architecture and format settings
ARCH = -f elf64
TARGET = hello_world
SOURCE = hello_world.asm

# Default build flags
ASMFLAGS = $(ARCH)
LDFLAGS = 

# Build targets
.PHONY: all debug release static clean install analyze disassemble hexdump run info

# Default target
all: $(TARGET)

# Build the main executable
$(TARGET): $(SOURCE)
	$(ASM) $(ASMFLAGS) -o $(TARGET).o $(SOURCE)
	$(LD) $(LDFLAGS) -o $(TARGET) $(TARGET).o

# Debug build with symbols
debug: ASMFLAGS = $(ARCH) -g -F dwarf
debug: LDFLAGS = 
debug: TARGET = hello_world_debug
debug: $(TARGET)

# Release build (optimized)
release: ASMFLAGS = $(ARCH) -O2
release: LDFLAGS = -s
release: $(TARGET)

# Static build
static: ASMFLAGS = $(ARCH) -O2
static: LDFLAGS = -static -s
static: $(TARGET)

# 32-bit build (if needed)
build32: ARCH = -f elf32
build32: LD = ld -m elf_i386
build32: TARGET = hello_world_32
build32: $(TARGET)

# Run the program
run: $(TARGET)
	./$(TARGET)

# Run with timing
time-run: $(TARGET)
	time ./$(TARGET)

# Display program information
info: $(TARGET)
	@echo "=== Binary Information ==="
	file $(TARGET)
	@echo
	@echo "=== Binary Size ==="
	ls -lh $(TARGET)
	@echo
	@echo "=== Sections ==="
	readelf -S $(TARGET) 2>/dev/null || echo "readelf not available"

# Disassemble the binary
disassemble: $(TARGET)
	$(OBJDUMP) -d $(TARGET) > $(TARGET).dis
	@echo "Disassembly saved to $(TARGET).dis"

# Create hex dump
hexdump: $(TARGET)
	$(HEXDUMP) -C $(TARGET) > $(TARGET).hex
	@echo "Hex dump saved to $(TARGET).hex"

# Static analysis (basic)
analyze: $(SOURCE)
	@echo "=== Assembly Source Analysis ==="
	@echo "Lines of code:"
	wc -l $(SOURCE)
	@echo "Instruction count (approximate):"
	grep -c "^\s*[a-z]" $(SOURCE) || echo "0"
	@echo "Labels count:"
	grep -c ":" $(SOURCE) || echo "0"

# Performance test
perf-test: $(TARGET)
	@echo "Running performance test..."
	@echo "=== Execution Time ==="
	time -p ./$(TARGET)
	@echo "=== System Call Trace ==="
	strace -c ./$(TARGET) 2>&1 | head -20 || echo "strace not available"

# Memory analysis
mem-analysis: $(TARGET)
	@echo "=== Memory Layout ==="
	size $(TARGET) 2>/dev/null || echo "size command not available"
	@echo "=== Virtual Memory Map ==="
	cat /proc/sys/vm/mmap_min_addr 2>/dev/null || echo "VM info not available"

# Install to system
install: $(TARGET)
	install -d /usr/local/bin
	install -m 755 $(TARGET) /usr/local/bin/

# Clean build artifacts
clean:
	rm -f $(TARGET) $(TARGET).o $(TARGET).dis $(TARGET).hex
	rm -f hello_world_debug hello_world_debug.o
	rm -f hello_world_32 hello_world_32.o

# Help target
help:
	@echo "Available targets:"
	@echo "  all          - Build default executable"
	@echo "  debug        - Build with debug symbols"
	@echo "  release      - Build optimized version"
	@echo "  static       - Build statically linked version"
	@echo "  build32      - Build 32-bit version"
	@echo "  run          - Run the program"
	@echo "  time-run     - Run with timing information"
	@echo "  info         - Display binary information"
	@echo "  disassemble  - Create disassembly listing"
	@echo "  hexdump      - Create hex dump"
	@echo "  analyze      - Basic source code analysis"
	@echo "  perf-test    - Performance testing"
	@echo "  mem-analysis - Memory layout analysis"
	@echo "  install      - Install to system"
	@echo "  clean        - Remove build artifacts"
	@echo "  help         - Show this help"
