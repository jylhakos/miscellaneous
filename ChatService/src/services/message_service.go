package services

import (
	"context"
	"errors"
	"math"
	"strings"
	"time"

	"chatservice/src/models"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// MessageService handles message operations
type MessageService struct {
	collection *mongo.Collection
}

// NewMessageService creates a new message service
func NewMessageService(db *mongo.Database, collectionName string) *MessageService {
	return &MessageService{
		collection: db.Collection(collectionName),
	}
}

// CreateMessage creates a new message
func (ms *MessageService) CreateMessage(ctx context.Context, req *models.CreateMessageRequest, ipAddress, userAgent string) (*models.Message, error) {
	message := &models.Message{
		ID:        primitive.NewObjectID(),
		Content:   req.Content,
		SenderID:  req.SenderID,
		Timestamp: time.Now(),
		Metadata: models.MessageMetadata{
			ReadStatus:  false,
			MessageType: req.MessageType,
			Priority:    req.Priority,
			Tags:        req.Tags,
			IPAddress:   ipAddress,
			UserAgent:   userAgent,
		},
	}

	if message.Metadata.Priority == "" {
		message.Metadata.Priority = "normal"
	}

	result, err := ms.collection.InsertOne(ctx, message)
	if err != nil {
		return nil, err
	}

	message.ID = result.InsertedID.(primitive.ObjectID)
	return message, nil
}

// GetMessage retrieves a message by ID
func (ms *MessageService) GetMessage(ctx context.Context, id string) (*models.Message, error) {
	objectID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return nil, errors.New("invalid message ID")
	}

	var message models.Message
	err = ms.collection.FindOne(ctx, bson.M{"_id": objectID}).Decode(&message)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return nil, errors.New("message not found")
		}
		return nil, err
	}

	return &message, nil
}

// ListMessages retrieves messages with pagination
func (ms *MessageService) ListMessages(ctx context.Context, page, limit int) (*models.ListMessagesResponse, error) {
	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 10
	}

	skip := (page - 1) * limit

	// Count total documents
	total, err := ms.collection.CountDocuments(ctx, bson.M{})
	if err != nil {
		return nil, err
	}

	// Find messages with pagination
	findOptions := options.Find()
	findOptions.SetLimit(int64(limit))
	findOptions.SetSkip(int64(skip))
	findOptions.SetSort(bson.D{{"timestamp", -1}}) // Sort by timestamp descending

	cursor, err := ms.collection.Find(ctx, bson.M{}, findOptions)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var messages []models.Message
	if err = cursor.All(ctx, &messages); err != nil {
		return nil, err
	}

	return &models.ListMessagesResponse{
		Messages: messages,
		Total:    total,
		Page:     page,
		Limit:    limit,
	}, nil
}

// DeleteMessage deletes a message by ID
func (ms *MessageService) DeleteMessage(ctx context.Context, id string) error {
	objectID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return errors.New("invalid message ID")
	}

	result, err := ms.collection.DeleteOne(ctx, bson.M{"_id": objectID})
	if err != nil {
		return err
	}

	if result.DeletedCount == 0 {
		return errors.New("message not found")
	}

	return nil
}

// CalculateAnomalyScore calculates anomaly score for spam detection
func (ms *MessageService) CalculateAnomalyScore(ctx context.Context, id string) (*models.AnomalyScore, error) {
	message, err := ms.GetMessage(ctx, id)
	if err != nil {
		return nil, err
	}

	score, reasons := ms.analyzeMessage(message)
	isSpam := score > 0.7 // Threshold for spam detection

	return &models.AnomalyScore{
		MessageID: message.ID,
		Score:     score,
		IsSpam:    isSpam,
		Reasons:   reasons,
		Timestamp: time.Now(),
	}, nil
}

// analyzeMessage performs simple spam analysis
func (ms *MessageService) analyzeMessage(message *models.Message) (float64, []string) {
	var score float64
	var reasons []string

	content := strings.ToLower(message.Content)

	// Check for spam keywords
	spamKeywords := []string{"free", "win", "urgent", "click here", "limited time", "act now"}
	keywordCount := 0
	for _, keyword := range spamKeywords {
		if strings.Contains(content, keyword) {
			keywordCount++
		}
	}

	if keywordCount > 0 {
		keywordScore := float64(keywordCount) / float64(len(spamKeywords))
		score += keywordScore * 0.4
		reasons = append(reasons, "Contains spam keywords")
	}

	// Check for excessive capitalization
	upperCount := 0
	for _, char := range message.Content {
		if char >= 'A' && char <= 'Z' {
			upperCount++
		}
	}
	if len(message.Content) > 0 {
		upperRatio := float64(upperCount) / float64(len(message.Content))
		if upperRatio > 0.5 {
			score += 0.3
			reasons = append(reasons, "Excessive capitalization")
		}
	}

	// Check for excessive exclamation marks
	exclamationCount := strings.Count(message.Content, "!")
	if exclamationCount > 3 {
		score += 0.2
		reasons = append(reasons, "Excessive exclamation marks")
	}

	// Check message length (very short messages might be spam)
	if len(strings.TrimSpace(message.Content)) < 10 {
		score += 0.1
		reasons = append(reasons, "Very short message")
	}

	// Ensure score doesn't exceed 1.0
	score = math.Min(score, 1.0)

	return score, reasons
}
