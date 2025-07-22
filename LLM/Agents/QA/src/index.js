// src/index.js
require("dotenv").config();
const express = require("express");
const cors = require("cors");
const { v4: uuidv4 } = require("uuid");
const { getAnswer, createSession, getSessionHistory, clearSession } = require("./qa");

const app = express();

// CORS configuration
const corsOptions = {
    origin: process.env.ALLOWED_ORIGINS ? process.env.ALLOWED_ORIGINS.split(',') : ['http://localhost:3001'],
    credentials: true,
    optionSuccessStatus: 200
};

app.use(cors(corsOptions));
app.use(express.json());

// Trust proxy for nginx reverse proxy
app.set('trust proxy', 1);

// Health check endpoint
app.get("/health", (req, res) => {
    res.json({ 
        status: "OK", 
        timestamp: new Date().toISOString(),
        service: "QA Chat Service"
    });
});

// Create new chat session
app.post("/api/session", (req, res) => {
    try {
        const sessionId = uuidv4();
        createSession(sessionId);
        res.json({ sessionId, message: "Session created successfully" });
    } catch (error) {
        console.error("Error creating session:", error);
        res.status(500).json({ error: "Failed to create session" });
    }
});

// GET endpoint for asking questions
app.get("/api/ask", async (req, res) => {
    const { question, sessionId } = req.query;
    
    if (!question) {
        return res.status(400).json({ error: "Question parameter is required" });
    }

    try {
        const answer = await getAnswer(question, sessionId);
        res.json({ 
            answer,
            sessionId: sessionId || 'default',
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error("Error handling question:", error);
        res.status(500).json({ error: "Failed to get answer" });
    }
});

// POST endpoint for asking questions (for Open WebUI compatibility)
app.post("/api/ask", async (req, res) => {
    const { question, sessionId } = req.body;
    
    if (!question) {
        return res.status(400).json({ error: "Question field is required" });
    }

    try {
        const answer = await getAnswer(question, sessionId);
        res.json({ 
            answer,
            sessionId: sessionId || 'default',
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error("Error handling question:", error);
        res.status(500).json({ error: "Failed to get answer" });
    }
});

// Get session history
app.get("/api/session/:sessionId/history", (req, res) => {
    const { sessionId } = req.params;
    
    try {
        const history = getSessionHistory(sessionId);
        res.json({ sessionId, history });
    } catch (error) {
        console.error("Error getting session history:", error);
        res.status(500).json({ error: "Failed to get session history" });
    }
});

// Clear session history
app.delete("/api/session/:sessionId", (req, res) => {
    const { sessionId } = req.params;
    
    try {
        clearSession(sessionId);
        res.json({ sessionId, message: "Session cleared successfully" });
    } catch (error) {
        console.error("Error clearing session:", error);
        res.status(500).json({ error: "Failed to clear session" });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: "Something went wrong!" });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: "Endpoint not found" });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log(`🚀 QA Chat Service running on port ${PORT}`);
    console.log(`🔗 Health check: http://localhost:${PORT}/health`);
    console.log(`💬 Ask endpoint: http://localhost:${PORT}/api/ask`);
    console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
});

module.exports = app;
