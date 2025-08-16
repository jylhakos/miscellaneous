/**
 * @file t.c
 * @brief Comprehensive C99 features demonstration
 * @date 2025-08-16
 * 
 * This file demonstrates modern C99 features including:
 * - Variable Length Arrays (VLAs)
 * - Designated initializers
 * - Compound literals
 * - Inline functions
 * - _Bool type
 * - long long type
 * - GCC vector extensions
 * - C99 comments
 * - Flexible array members
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <complex.h>
#include <inttypes.h>

// C99 compound literal and designated initializer
#define POINT_ZERO (struct point){.x = 0, .y = 0}

// GCC Vector extension (compatible with Clang)
typedef float V __attribute__((vector_size(16)));
typedef int int_vec __attribute__((vector_size(16)));

// C99 inline function
inline V vector_add(V a, V b) {
    return a + b;
}

inline V vector_multiply_add(V a, V b) {
    return a + b * a;
}

// Structure with flexible array member (C99)
struct dynamic_array {
    size_t length;
    int data[];  // Flexible array member
};

// Structure for demonstration
struct point {
    double x, y;
    _Bool is_valid;
};

struct color {
    uint8_t r, g, b, a;
};

// C99 complex numbers demonstration
void demonstrate_complex_numbers(void) {
    printf("\n=== C99 Complex Numbers ===\n");
    
    double complex z1 = 3.0 + 4.0 * I;
    double complex z2 = 1.0 + 2.0 * I;
    
    printf("z1 = %.2f + %.2fi\n", creal(z1), cimag(z1));
    printf("z2 = %.2f + %.2fi\n", creal(z2), cimag(z2));
    printf("z1 + z2 = %.2f + %.2fi\n", 
           creal(z1 + z2), cimag(z1 + z2));
    printf("Magnitude of z1: %.2f\n", cabs(z1));
}

// Variable Length Arrays (VLA) demonstration
void demonstrate_vla(int n) {
    printf("\n=== Variable Length Arrays ===\n");
    printf("Creating VLA of size %d\n", n);
    
    // C99 VLA declaration
    int matrix[n][n];
    
    // Initialize VLA
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            matrix[i][j] = i * n + j + 1;
        }
    }
    
    // Print matrix
    printf("Matrix %dx%d:\n", n, n);
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            printf("%3d ", matrix[i][j]);
        }
        printf("\n");
    }
}

// Designated initializers demonstration
void demonstrate_designated_initializers(void) {
    printf("\n=== C99 Designated Initializers ===\n");
    
    // Array with designated initializers
    int fibonacci[10] = {[0] = 0, [1] = 1, [2] = 1, [3] = 2, [4] = 3, [5] = 5};
    
    printf("Fibonacci sequence (partial): ");
    for (int i = 0; i < 10; i++) {
        printf("%d ", fibonacci[i]);
    }
    printf("\n");
    
    // Struct with designated initializers
    struct point p1 = {.x = 10.5, .y = 20.3, .is_valid = true};
    struct point p2 = {.y = 15.7, .x = 5.2, .is_valid = false};
    
    printf("Point 1: (%.1f, %.1f) Valid: %s\n", 
           p1.x, p1.y, p1.is_valid ? "true" : "false");
    printf("Point 2: (%.1f, %.1f) Valid: %s\n", 
           p2.x, p2.y, p2.is_valid ? "true" : "false");
    
    // Color with designated initializers
    struct color red = {.r = 255, .g = 0, .b = 0, .a = 255};
    struct color transparent_blue = {.b = 255, .a = 128};
    
    printf("Red color: RGBA(%d, %d, %d, %d)\n", 
           red.r, red.g, red.b, red.a);
    printf("Transparent blue: RGBA(%d, %d, %d, %d)\n", 
           transparent_blue.r, transparent_blue.g, 
           transparent_blue.b, transparent_blue.a);
}

// Vector operations demonstration
void demonstrate_vector_operations(void) {
    printf("\n=== GCC Vector Extensions ===\n");
    
    // Float vectors (4 floats in 16 bytes)
    V vec1 = {1.0f, 2.0f, 3.0f, 4.0f};
    V vec2 = {5.0f, 6.0f, 7.0f, 8.0f};
    
    V result_add = vector_add(vec1, vec2);
    V result_mul_add = vector_multiply_add(vec1, vec2);
    
    printf("vec1: [%.1f, %.1f, %.1f, %.1f]\n", 
           vec1[0], vec1[1], vec1[2], vec1[3]);
    printf("vec2: [%.1f, %.1f, %.1f, %.1f]\n", 
           vec2[0], vec2[1], vec2[2], vec2[3]);
    printf("vec1 + vec2: [%.1f, %.1f, %.1f, %.1f]\n", 
           result_add[0], result_add[1], result_add[2], result_add[3]);
    printf("vec1 + vec2*vec1: [%.1f, %.1f, %.1f, %.1f]\n", 
           result_mul_add[0], result_mul_add[1], 
           result_mul_add[2], result_mul_add[3]);
    
    // Integer vectors
    int_vec ivec1 = {1, 2, 3, 4};
    int_vec ivec2 = {10, 20, 30, 40};
    int_vec ivec_sum = ivec1 + ivec2;
    
    printf("Integer vector sum: [%d, %d, %d, %d]\n",
           ivec_sum[0], ivec_sum[1], ivec_sum[2], ivec_sum[3]);
}

// Compound literals demonstration
void demonstrate_compound_literals(void) {
    printf("\n=== C99 Compound Literals ===\n");
    
    // Function call with compound literal
    struct point *p = &(struct point){.x = 100.0, .y = 200.0, .is_valid = true};
    
    printf("Compound literal point: (%.1f, %.1f)\n", p->x, p->y);
    
    // Array compound literal
    int *arr = (int[]){1, 1, 2, 3, 5, 8, 13, 21};
    printf("Compound literal array: ");
    for (int i = 0; i < 8; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

// Dynamic array with flexible array member
struct dynamic_array *create_dynamic_array(size_t length) {
    struct dynamic_array *arr = malloc(sizeof(struct dynamic_array) + 
                                     sizeof(int) * length);
    if (arr != NULL) {
        arr->length = length;
        for (size_t i = 0; i < length; i++) {
            arr->data[i] = (int)(i * i);  // Square numbers
        }
    }
    return arr;
}

void demonstrate_flexible_array_member(void) {
    printf("\n=== C99 Flexible Array Members ===\n");
    
    struct dynamic_array *arr = create_dynamic_array(7);
    if (arr != NULL) {
        printf("Dynamic array (squares): ");
        for (size_t i = 0; i < arr->length; i++) {
            printf("%d ", arr->data[i]);
        }
        printf("\n");
        free(arr);
    }
}

// C99 Standard integer types
void demonstrate_stdint_types(void) {
    printf("\n=== C99 Standard Integer Types ===\n");
    
    int8_t i8 = -128;
    uint8_t u8 = 255;
    int16_t i16 = -32768;
    uint16_t u16 = 65535;
    int32_t i32 = -2147483648;
    uint32_t u32 = 4294967295U;
    int64_t i64 = -9223372036854775807LL - 1;
    uint64_t u64 = 18446744073709551615ULL;
    
    printf("int8_t:   %" PRId8 "\n", i8);
    printf("uint8_t:  %" PRIu8 "\n", u8);
    printf("int16_t:  %" PRId16 "\n", i16);
    printf("uint16_t: %" PRIu16 "\n", u16);
    printf("int32_t:  %" PRId32 "\n", i32);
    printf("uint32_t: %" PRIu32 "\n", u32);
    printf("int64_t:  %" PRId64 "\n", i64);
    printf("uint64_t: %" PRIu64 "\n", u64);
    
    printf("Size of long long: %zu bytes\n", sizeof(long long));
}

// _Bool type demonstration
void demonstrate_bool_type(void) {
    printf("\n=== C99 _Bool Type ===\n");
    
    _Bool flag1 = 1;
    _Bool flag2 = 0;
    bool flag3 = true;   // Using stdbool.h
    bool flag4 = false;
    
    printf("_Bool flag1 (1): %d\n", flag1);
    printf("_Bool flag2 (0): %d\n", flag2);
    printf("bool flag3 (true): %d\n", flag3);
    printf("bool flag4 (false): %d\n", flag4);
    printf("Size of _Bool: %zu bytes\n", sizeof(_Bool));
    
    // _Bool in expressions
    int x = 5, y = 10;
    _Bool comparison = (x < y);
    printf("(5 < 10) = %s\n", comparison ? "true" : "false");
}

int main(int argc, char **argv) {
    printf("===== Comprehensive C99 Features Demonstration =====\n");
    printf("Compiled with: %s\n", 
#ifdef __GNUC__
           "GCC " __VERSION__
#elif defined(__clang__)
           "Clang " __clang_version__
#else
           "Unknown compiler"
#endif
    );
    
    printf("C Standard: ");
#if __STDC_VERSION__ >= 199901L
    printf("C99 or later (__STDC_VERSION__ = %ld)\n", __STDC_VERSION__);
#else
    printf("Pre-C99 (__STDC_VERSION__ = %ld)\n", __STDC_VERSION__);
#endif

    // Demonstrate all C99 features
    demonstrate_complex_numbers();
    demonstrate_vla(4);
    demonstrate_designated_initializers();
    demonstrate_vector_operations();
    demonstrate_compound_literals();
    demonstrate_flexible_array_member();
    demonstrate_stdint_types();
    demonstrate_bool_type();
    
    printf("\n===== End of C99 Demonstration =====\n");
    return 0;
}
