package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// Message represents a single message with its metadata
type Message struct {
	ID        primitive.ObjectID `json:"id,omitempty" bson:"_id,omitempty"`
	Content   string             `json:"content" bson:"content" validate:"required,min=1,max=2000"`
	SenderID  string             `json:"sender_id" bson:"sender_id" validate:"required"`
	Timestamp time.Time          `json:"timestamp" bson:"timestamp"`
	Metadata  MessageMetadata    `json:"metadata" bson:"metadata"`
}

// MessageMetadata contains additional information about the message
type MessageMetadata struct {
	ReadStatus  bool     `json:"read_status" bson:"read_status"`
	MessageType string   `json:"message_type" bson:"message_type" validate:"required,oneof=text image file"`
	Priority    string   `json:"priority,omitempty" bson:"priority,omitempty" validate:"omitempty,oneof=low normal high"`
	Tags        []string `json:"tags,omitempty" bson:"tags,omitempty"`
	IPAddress   string   `json:"ip_address,omitempty" bson:"ip_address,omitempty"`
	UserAgent   string   `json:"user_agent,omitempty" bson:"user_agent,omitempty"`
}

// CreateMessageRequest represents the request payload for creating a message
type CreateMessageRequest struct {
	Content     string   `json:"content" validate:"required,min=1,max=2000"`
	SenderID    string   `json:"sender_id" validate:"required"`
	MessageType string   `json:"message_type" validate:"required,oneof=text image file"`
	Priority    string   `json:"priority,omitempty" validate:"omitempty,oneof=low normal high"`
	Tags        []string `json:"tags,omitempty"`
}

// AnomalyScore represents the anomaly detection result for a message
type AnomalyScore struct {
	MessageID primitive.ObjectID `json:"message_id"`
	Score     float64            `json:"score"`
	IsSpam    bool               `json:"is_spam"`
	Reasons   []string           `json:"reasons,omitempty"`
	Timestamp time.Time          `json:"timestamp"`
}

// ErrorResponse represents an error response
type ErrorResponse struct {
	Error   string      `json:"error"`
	Message string      `json:"message"`
	Details interface{} `json:"details,omitempty"`
}

// ListMessagesResponse represents the response for listing messages
type ListMessagesResponse struct {
	Messages []Message `json:"messages"`
	Total    int64     `json:"total"`
	Page     int       `json:"page"`
	Limit    int       `json:"limit"`
}
