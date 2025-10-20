// MongoDB initialization script
db = db.getSiblingDB('chatservice');

// Create indexes for performance
db.messages.createIndex({ "timestamp": -1 });
db.messages.createIndex({ "sender_id": 1 });
db.messages.createIndex({ "metadata.message_type": 1 });

// Insert sample data for testing
db.messages.insertMany([
  {
    content: "Hello, this is a test message!",
    sender_id: "user123",
    timestamp: new Date(),
    metadata: {
      read_status: false,
      message_type: "text",
      priority: "normal",
      tags: ["greeting", "test"],
      ip_address: "127.0.0.1",
      user_agent: "Test Agent"
    }
  },
  {
    content: "Another test message with different priority",
    sender_id: "user456",
    timestamp: new Date(),
    metadata: {
      read_status: true,
      message_type: "text", 
      priority: "high",
      tags: ["urgent"],
      ip_address: "127.0.0.1",
      user_agent: "Test Agent"
    }
  }
]);

print("Database initialized with sample data");