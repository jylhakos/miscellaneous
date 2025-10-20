package config

import (
	"os"
	"strconv"
)

// Config holds the application configuration
type Config struct {
	MongoDB   MongoDBConfig
	Server    ServerConfig
	JWT       JWTConfig
	RateLimit RateLimitConfig
}

// MongoDBConfig holds MongoDB configuration
type MongoDBConfig struct {
	URI        string
	Database   string
	Collection string
}

// ServerConfig holds server configuration
type ServerConfig struct {
	Port string
	Host string
}

// JWTConfig holds JWT configuration
type JWTConfig struct {
	SecretKey   string
	Issuer      string
	ExpiryHours int
}

// RateLimitConfig holds rate limiting configuration
type RateLimitConfig struct {
	RequestsPerMinute int
	BurstSize         int
}

// Load loads configuration from environment variables with defaults
func Load() *Config {
	return &Config{
		MongoDB: MongoDBConfig{
			URI:        getEnv("MONGODB_URI", "mongodb://localhost:27017"),
			Database:   getEnv("MONGODB_DATABASE", "chatservice"),
			Collection: getEnv("MONGODB_COLLECTION", "messages"),
		},
		Server: ServerConfig{
			Port: getEnv("SERVER_PORT", "8080"),
			Host: getEnv("SERVER_HOST", "0.0.0.0"),
		},
		JWT: JWTConfig{
			SecretKey:   getEnv("JWT_SECRET_KEY", "your-secret-key-change-in-production"),
			Issuer:      getEnv("JWT_ISSUER", "chatservice"),
			ExpiryHours: getEnvAsInt("JWT_EXPIRY_HOURS", 24),
		},
		RateLimit: RateLimitConfig{
			RequestsPerMinute: getEnvAsInt("RATE_LIMIT_RPM", 100),
			BurstSize:         getEnvAsInt("RATE_LIMIT_BURST", 10),
		},
	}
}

// getEnv gets environment variable with default value
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// getEnvAsInt gets environment variable as integer with default value
func getEnvAsInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}
