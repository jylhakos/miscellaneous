package handlers

import (
	"net/http"
	"strconv"

	"chatservice/src/models"
	"chatservice/src/services"

	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
)

// MessageHandler handles HTTP requests for messages
type MessageHandler struct {
	messageService *services.MessageService
	validator      *validator.Validate
}

// NewMessageHandler creates a new message handler
func NewMessageHandler(messageService *services.MessageService) *MessageHandler {
	return &MessageHandler{
		messageService: messageService,
		validator:      validator.New(),
	}
}

// CreateMessage creates a new message
func (h *MessageHandler) CreateMessage(c *gin.Context) {
	var req models.CreateMessageRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "invalid_request",
			Message: "Invalid request body",
			Details: err.Error(),
		})
		return
	}

	// Validate request
	if err := h.validator.Struct(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "validation_error",
			Message: "Request validation failed",
			Details: err.Error(),
		})
		return
	}

	// Get client information
	ipAddress := c.ClientIP()
	userAgent := c.GetHeader("User-Agent")

	// Create message
	message, err := h.messageService.CreateMessage(c.Request.Context(), &req, ipAddress, userAgent)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Error:   "internal_error",
			Message: "Failed to create message",
			Details: err.Error(),
		})
		return
	}

	c.Header("Content-Type", "application/json")
	c.JSON(http.StatusCreated, message)
}

// GetMessage retrieves a message by ID
func (h *MessageHandler) GetMessage(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "invalid_request",
			Message: "Message ID is required",
		})
		return
	}

	message, err := h.messageService.GetMessage(c.Request.Context(), id)
	if err != nil {
		if err.Error() == "message not found" {
			c.JSON(http.StatusNotFound, models.ErrorResponse{
				Error:   "not_found",
				Message: "Message not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Error:   "internal_error",
			Message: "Failed to retrieve message",
			Details: err.Error(),
		})
		return
	}

	c.Header("Content-Type", "application/json")
	c.JSON(http.StatusOK, message)
}

// ListMessages retrieves messages with pagination
func (h *MessageHandler) ListMessages(c *gin.Context) {
	page := 1
	limit := 10

	if pageStr := c.Query("page"); pageStr != "" {
		if p, err := strconv.Atoi(pageStr); err == nil && p > 0 {
			page = p
		}
	}

	if limitStr := c.Query("limit"); limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil && l > 0 && l <= 100 {
			limit = l
		}
	}

	response, err := h.messageService.ListMessages(c.Request.Context(), page, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Error:   "internal_error",
			Message: "Failed to retrieve messages",
			Details: err.Error(),
		})
		return
	}

	c.Header("Content-Type", "application/json")
	c.JSON(http.StatusOK, response)
}

// DeleteMessage deletes a message by ID
func (h *MessageHandler) DeleteMessage(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "invalid_request",
			Message: "Message ID is required",
		})
		return
	}

	err := h.messageService.DeleteMessage(c.Request.Context(), id)
	if err != nil {
		if err.Error() == "message not found" {
			c.JSON(http.StatusNotFound, models.ErrorResponse{
				Error:   "not_found",
				Message: "Message not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Error:   "internal_error",
			Message: "Failed to delete message",
			Details: err.Error(),
		})
		return
	}

	c.JSON(http.StatusNoContent, nil)
}

// GetAnomalyScore calculates and returns anomaly score for a message
func (h *MessageHandler) GetAnomalyScore(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "invalid_request",
			Message: "Message ID is required",
		})
		return
	}

	anomalyScore, err := h.messageService.CalculateAnomalyScore(c.Request.Context(), id)
	if err != nil {
		if err.Error() == "message not found" {
			c.JSON(http.StatusNotFound, models.ErrorResponse{
				Error:   "not_found",
				Message: "Message not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Error:   "internal_error",
			Message: "Failed to calculate anomaly score",
			Details: err.Error(),
		})
		return
	}

	c.Header("Content-Type", "application/json")
	c.JSON(http.StatusOK, anomalyScore)
}

// HealthCheck returns the health status of the service
func (h *MessageHandler) HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "healthy",
		"timestamp": c.Request.Context().Value("timestamp"),
		"version":   "1.0.0",
	})
}
