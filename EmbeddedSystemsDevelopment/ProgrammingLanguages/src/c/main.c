#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/time.h>
#include <math.h>
#include <stdint.h>

/* Performance timer structure */
typedef struct {
    struct timeval start_time;
    struct timeval end_time;
} performance_timer_t;

/* Application context structure */
typedef struct {
    struct timeval app_start_time;
    const char* version;
} hello_app_t;

/* Initialize performance timer */
void timer_start(performance_timer_t* timer) {
    gettimeofday(&timer->start_time, NULL);
}

/* Stop performance timer */
void timer_stop(performance_timer_t* timer) {
    gettimeofday(&timer->end_time, NULL);
}

/* Get duration in microseconds */
long timer_get_duration_us(const performance_timer_t* timer) {
    return (timer->end_time.tv_sec - timer->start_time.tv_sec) * 1000000L +
           (timer->end_time.tv_usec - timer->start_time.tv_usec);
}

/* Get duration in milliseconds */
long timer_get_duration_ms(const performance_timer_t* timer) {
    return timer_get_duration_us(timer) / 1000;
}

/* Initialize application */
void app_init(hello_app_t* app) {
    gettimeofday(&app->app_start_time, NULL);
    app->version = "1.0.0";
    
    printf("C Hello World Application initialized\n");
    printf("Optimized for RTOS deployment\n");
    printf("Version: %s\n", app->version);
    printf("Build timestamp: %s %s\n", __DATE__, __TIME__);
    printf("----------------------------------------\n\n");
}

/* Display hello message */
void display_hello(const hello_app_t* app) {
    struct timeval now;
    gettimeofday(&now, NULL);
    
    long elapsed_ms = (now.tv_sec - app->app_start_time.tv_sec) * 1000L +
                     (now.tv_usec - app->app_start_time.tv_usec) / 1000;
    
    printf("Hello World from C!\n");
    printf("Runtime: %ld ms\n", elapsed_ms);
    printf("Process ID: %d\n\n", getpid());
}

/* Integer performance test */
void perf_test_integer(void) {
    const int iterations = 1000000;
    performance_timer_t timer;
    volatile long long result = 0;
    
    printf("Integer Operations Test:\n");
    
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        result += i * 2;
    }
    timer_stop(&timer);
    
    long duration_us = timer_get_duration_us(&timer);
    double ops_per_sec = (double)iterations / (duration_us / 1000000.0);
    
    printf("  Iterations: %d\n", iterations);
    printf("  Time: %ld μs\n", duration_us);
    printf("  Rate: %.0f ops/sec\n", ops_per_sec);
    printf("  Result: %lld\n\n", result);
}

/* Floating-point performance test */
void perf_test_floating_point(void) {
    const int iterations = 1000000;
    performance_timer_t timer;
    volatile double result = 0.0;
    
    printf("Floating-Point Operations Test (sin/cos):\n");
    
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        result += sin(i * 0.001) * cos(i * 0.001);
    }
    timer_stop(&timer);
    
    long duration_us = timer_get_duration_us(&timer);
    double ops_per_sec = (double)iterations / (duration_us / 1000000.0);
    
    printf("  Iterations: %d\n", iterations);
    printf("  Time: %ld μs\n", duration_us);
    printf("  Rate: %.0f ops/sec\n", ops_per_sec);
    printf("  Result: %.6f\n\n", result);
}

/* Memory performance test */
void perf_test_memory(void) {
    const int size = 1000;
    performance_timer_t timer;
    int* memory_test = NULL;
    
    printf("Memory Operations Test (malloc/access):\n");
    
    timer_start(&timer);
    
    /* Allocate memory */
    memory_test = (int*)malloc(size * sizeof(int));
    if (memory_test == NULL) {
        printf("  ERROR: Memory allocation failed\n\n");
        return;
    }
    
    /* Initialize array */
    for (int i = 0; i < size; i++) {
        memory_test[i] = i * i;
    }
    
    /* Calculate sum (to ensure memory access) */
    volatile long long sum = 0;
    for (int i = 0; i < size; i++) {
        sum += memory_test[i];
    }
    
    timer_stop(&timer);
    
    long duration_us = timer_get_duration_us(&timer);
    double ops_per_sec = (double)size / (duration_us / 1000000.0);
    
    printf("  Elements: %d\n", size);
    printf("  Time: %ld μs\n", duration_us);
    printf("  Rate: %.0f ops/sec\n", ops_per_sec);
    printf("  Sum: %lld\n\n", sum);
    
    free(memory_test);
}

/* Run all performance tests */
void run_performance_tests(void) {
    printf("Starting C Performance Tests...\n\n");
    
    perf_test_integer();
    perf_test_floating_point();
    perf_test_memory();
}

/* Display system information */
void display_system_info(void) {
    printf("System Information:\n");
    printf("  C Standard: ");
    
#if __STDC_VERSION__ >= 201710L
    printf("C18");
#elif __STDC_VERSION__ >= 201112L
    printf("C11");
#elif __STDC_VERSION__ >= 199901L
    printf("C99");
#elif defined(__STDC__)
    printf("C89/C90");
#else
    printf("Pre-standard C");
#endif
    
    printf("\n");
    
    printf("  Compiler: ");
#ifdef __GNUC__
    printf("GCC %d.%d.%d", __GNUC__, __GNUC_MINOR__, __GNUC_PATCHLEVEL__);
#elif defined(__clang__)
    printf("Clang %d.%d.%d", __clang_major__, __clang_minor__, __clang_patchlevel__);
#elif defined(_MSC_VER)
    printf("MSVC %d", _MSC_VER);
#else
    printf("Unknown");
#endif
    printf("\n");
    
    printf("  Pointer size: %lu bits\n", sizeof(void*) * 8);
    printf("  int size: %lu bytes\n", sizeof(int));
    printf("  long size: %lu bytes\n", sizeof(long));
    printf("  double size: %lu bytes\n", sizeof(double));
    printf("\n");
}

/* Display help information */
void display_help(const char* program_name) {
    printf("Usage: %s [options]\n", program_name);
    printf("Options:\n");
    printf("  --hello    Display hello message and exit\n");
    printf("  --perf     Run performance test and exit\n");
    printf("  --info     Display system information and exit\n");
    printf("  --help     Display this help message\n");
    printf("  (no args)  Run interactive menu\n");
}

/* Interactive menu */
void run_interactive_menu(hello_app_t* app) {
    char input[10];
    int choice;
    
    while (1) {
        printf("C Hello World Menu:\n");
        printf("1. Display Hello Message\n");
        printf("2. Run Performance Test\n");
        printf("3. Display System Info\n");
        printf("4. Exit\n");
        printf("Enter choice (1-4): ");
        
        if (fgets(input, sizeof(input), stdin) == NULL) {
            printf("Error reading input\n");
            continue;
        }
        
        choice = atoi(input);
        
        switch (choice) {
            case 1:
                display_hello(app);
                break;
            case 2:
                run_performance_tests();
                break;
            case 3:
                display_system_info();
                break;
            case 4:
                printf("Goodbye!\n");
                return;
            default:
                printf("Invalid choice. Please try again.\n\n");
                break;
        }
    }
}

/* Main function */
int main(int argc, char* argv[]) {
    hello_app_t app;
    
    printf("Starting C Hello World Application...\n");
    printf("Arguments: %d\n", argc);
    
    for (int i = 0; i < argc; i++) {
        printf("  argv[%d]: %s\n", i, argv[i]);
    }
    printf("\n");
    
    /* Process command-line arguments */
    if (argc > 1) {
        if (strcmp(argv[1], "--hello") == 0) {
            app_init(&app);
            display_hello(&app);
            return 0;
        } else if (strcmp(argv[1], "--perf") == 0) {
            app_init(&app);
            run_performance_tests();
            return 0;
        } else if (strcmp(argv[1], "--info") == 0) {
            app_init(&app);
            display_system_info();
            return 0;
        } else if (strcmp(argv[1], "--help") == 0) {
            display_help(argv[0]);
            return 0;
        } else {
            printf("Unknown option: %s\n", argv[1]);
            display_help(argv[0]);
            return 1;
        }
    }
    
    /* Run interactive menu by default */
    app_init(&app);
    run_interactive_menu(&app);
    
    return 0;
}
