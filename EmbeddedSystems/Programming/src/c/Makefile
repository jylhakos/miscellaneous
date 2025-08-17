CC = gcc
CFLAGS = -std=c99 -Wall -Wextra -O2 -g
LDFLAGS = -lm
TARGET = c_hello_world
SOURCE = main.c

# Default target
all: $(TARGET)

# Build the main executable
$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE) $(LDFLAGS)

# Debug build
debug: CFLAGS = -std=c99 -Wall -Wextra -O0 -g -DDEBUG
debug: LDFLAGS = -lm
debug: $(TARGET)

# Release build with maximum optimization
release: CFLAGS = -std=c99 -Wall -Wextra -O3 -DNDEBUG -march=native
release: LDFLAGS = -lm
release: $(TARGET)

# Static build for deployment
static: CFLAGS = -std=c99 -Wall -Wextra -O2 -static
static: LDFLAGS = -lm
static: $(TARGET)

# Cross-compilation for ARM
arm: CC = arm-linux-gnueabihf-gcc
arm: CFLAGS = -std=c99 -Wall -Wextra -O2 -static
arm: LDFLAGS = -lm
arm: TARGET = c_hello_world_arm
arm: $(TARGET)

# Performance profiling build
profile: CFLAGS = -std=c99 -Wall -Wextra -O2 -g -pg
profile: LDFLAGS = -lm
profile: $(TARGET)

# Strict compilation with all warnings
strict: CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Werror -O2 -g
strict: LDFLAGS = -lm
strict: $(TARGET)

# Minimal build (for embedded systems)
minimal: CFLAGS = -std=c99 -Os -ffunction-sections -fdata-sections -Wl,--gc-sections
minimal: LDFLAGS = -lm
minimal: $(TARGET)

# Run the application
run: $(TARGET)
	./$(TARGET)

# Run performance test
perf-test: $(TARGET)
	./$(TARGET) --perf

# Clean build artifacts
clean:
	rm -f $(TARGET) c_hello_world_arm gmon.out

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

# Memory check with valgrind
memcheck: $(TARGET)
	valgrind --leak-check=full --track-origins=yes ./$(TARGET) --perf

# Static analysis with cppcheck
analyze:
	cppcheck --enable=all --std=c99 $(SOURCE)

.PHONY: all debug release static arm profile strict minimal run perf-test clean install deploy memcheck analyze
