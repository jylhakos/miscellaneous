package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"chatservice/src/config"
	"chatservice/src/handlers"
	"chatservice/src/middleware"
	"chatservice/src/services"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func main() {
	// Load configuration
	cfg := config.Load()

	// Connect to MongoDB
	client, err := connectMongoDB(cfg.MongoDB.URI)
	if err != nil {
		log.Fatal("Failed to connect to MongoDB:", err)
	}
	defer client.Disconnect(context.Background())

	// Initialize database and services
	db := client.Database(cfg.MongoDB.Database)
	messageService := services.NewMessageService(db, cfg.MongoDB.Collection)

	// Initialize handlers
	messageHandler := handlers.NewMessageHandler(messageService)

	// Initialize rate limiter
	rateLimiter := middleware.NewRateLimiter(cfg.RateLimit.RequestsPerMinute, cfg.RateLimit.BurstSize)

	// Setup router
	router := setupRouter(messageHandler, rateLimiter, cfg)

	// Create HTTP server
	server := &http.Server{
		Addr:    fmt.Sprintf("%s:%s", cfg.Server.Host, cfg.Server.Port),
		Handler: router,
	}

	// Start server in a goroutine
	go func() {
		log.Printf("Starting server on %s:%s", cfg.Server.Host, cfg.Server.Port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal("Failed to start server:", err)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown the server
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")

	// Graceful shutdown with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		log.Fatal("Server forced to shutdown:", err)
	}

	log.Println("Server exited")
}

func connectMongoDB(uri string) (*mongo.Client, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	clientOptions := options.Client().ApplyURI(uri)
	client, err := mongo.Connect(ctx, clientOptions)
	if err != nil {
		return nil, err
	}

	// Ping the database to verify connection
	if err := client.Ping(ctx, nil); err != nil {
		return nil, err
	}

	log.Println("Connected to MongoDB")
	return client, nil
}

func setupRouter(messageHandler *handlers.MessageHandler, rateLimiter *middleware.RateLimiter, cfg *config.Config) *gin.Engine {
	// Set Gin mode
	gin.SetMode(gin.ReleaseMode)

	router := gin.New()

	// Add middleware
	router.Use(middleware.RequestLogger())
	router.Use(middleware.CORS())
	router.Use(middleware.SecurityHeaders())
	router.Use(rateLimiter.Middleware())
	router.Use(gin.Recovery())

	// Health check endpoint (no auth required)
	router.GET("/health", messageHandler.HealthCheck)

	// API v1 routes
	v1 := router.Group("/v1")
	{
		// Public endpoints (no auth required for demo purposes)
		// In production, you might want to add JWT middleware
		messages := v1.Group("/messages")
		{
			messages.POST("", messageHandler.CreateMessage)
			messages.GET("", messageHandler.ListMessages)
			messages.GET("/:id", messageHandler.GetMessage)
			messages.DELETE("/:id", messageHandler.DeleteMessage)
			messages.GET("/:id/anomaly-check", messageHandler.GetAnomalyScore)
		}

		// Protected endpoints (with JWT authentication)
		// Uncomment the following lines to enable JWT authentication
		// protected := v1.Group("/admin")
		// protected.Use(middleware.JWTMiddleware(cfg))
		// {
		//     protected.GET("/stats", messageHandler.GetStats)
		// }
	}

	return router
}
