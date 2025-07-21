// src/memory.js

const { createClient } = require('redis');
require('dotenv').config();

// Session configuration
const SESSION_CONFIG = {
    // Session duration in seconds
    SESSION_DURATION: parseInt(process.env.SESSION_DURATION) || 1800, // 30 minutes default
    // Maximum conversations per session
    MAX_CONVERSATIONS_PER_SESSION: parseInt(process.env.MAX_CONVERSATIONS_PER_SESSION) || 20,
    // Session cleanup interval in milliseconds
    CLEANUP_INTERVAL: parseInt(process.env.CLEANUP_INTERVAL) || 300000, // 5 minutes default
    // Session inactivity timeout in seconds
    INACTIVITY_TIMEOUT: parseInt(process.env.INACTIVITY_TIMEOUT) || 900, // 15 minutes default
};

class SessionMemoryStore {
    constructor(useRedis = true) {
        this.store = new Map(); // Fallback to in-memory storage
        this.sessions = new Map(); // Track active sessions
        this.redisClient = null;
        this.initialized = false;
        this.useRedis = useRedis && process.env.NODE_ENV !== 'test';
        this.redisConnected = false;
        this.cleanupInterval = null;
        
        // Start cleanup timer
        this.startCleanupTimer();
    }

    /**
     * Generate a session ID for a user
     */
    generateSessionId(userId) {
        const timestamp = Date.now();
        return `session:${userId}:${timestamp}`;
    }

    /**
     * Get or create a session for a user
     */
    async getOrCreateSession(userId) {
        const userSessions = await this.getUserActiveSessions(userId);
        
        // Check if there's an active session within timeout
        for (const sessionData of userSessions) {
            const timeSinceLastActivity = Date.now() - sessionData.lastActivity;
            if (timeSinceLastActivity < SESSION_CONFIG.INACTIVITY_TIMEOUT * 1000) {
                // Update last activity
                sessionData.lastActivity = Date.now();
                await this.updateSession(sessionData);
                return sessionData.sessionId;
            }
        }
        
        // Create new session
        const sessionId = this.generateSessionId(userId);
        const sessionData = {
            sessionId,
            userId,
            startTime: Date.now(),
            lastActivity: Date.now(),
            conversationCount: 0,
            status: 'active'
        };
        
        await this.saveSession(sessionData);
        console.log(`Created new session for user ${userId}: ${sessionId}`);
        return sessionId;
    }

    /**
     * Save session data
     */
    async saveSession(sessionData) {
        const sessionKey = `session_data:${sessionData.sessionId}`;
        const userSessionsKey = `user_sessions:${sessionData.userId}`;
        
        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                // Save session data
                await this.redisClient.setEx(
                    sessionKey,
                    SESSION_CONFIG.SESSION_DURATION,
                    JSON.stringify(sessionData)
                );
                
                // Add to user's session list
                await this.redisClient.sAdd(userSessionsKey, sessionData.sessionId);
                await this.redisClient.expire(userSessionsKey, SESSION_CONFIG.SESSION_DURATION);
                
                return;
            } catch (error) {
                console.log(`Redis save session error: ${error.message}`);
            }
        }
        
        // Fallback to memory
        this.sessions.set(sessionData.sessionId, sessionData);
    }

    /**
     * Update session data
     */
    async updateSession(sessionData) {
        await this.saveSession(sessionData);
    }

    /**
     * Get user's active sessions
     */
    async getUserActiveSessions(userId) {
        const userSessionsKey = `user_sessions:${userId}`;
        let sessionIds = [];
        
        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                sessionIds = await this.redisClient.sMembers(userSessionsKey);
            } catch (error) {
                console.log(`Redis get user sessions error: ${error.message}`);
            }
        } else {
            // Fallback: find sessions in memory
            sessionIds = Array.from(this.sessions.keys()).filter(id => id.includes(userId));
        }
        
        const sessions = [];
        for (const sessionId of sessionIds) {
            const sessionData = await this.getSession(sessionId);
            if (sessionData && sessionData.status === 'active') {
                sessions.push(sessionData);
            }
        }
        
        return sessions;
    }

    /**
     * Get session data
     */
    async getSession(sessionId) {
        const sessionKey = `session_data:${sessionId}`;
        
        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                const sessionData = await this.redisClient.get(sessionKey);
                return sessionData ? JSON.parse(sessionData) : null;
            } catch (error) {
                console.log(`Redis get session error: ${error.message}`);
            }
        }
        
        return this.sessions.get(sessionId) || null;
    }

    /**
     * End a session and cleanup its data
     */
    async endSession(sessionId, reason = 'manual') {
        console.log(`Ending session ${sessionId} (reason: ${reason})`);
        
        const sessionData = await this.getSession(sessionId);
        if (!sessionData) return;
        
        // Mark session as ended
        sessionData.status = 'ended';
        sessionData.endTime = Date.now();
        sessionData.endReason = reason;
        
        // Save final session state (brief retention for logging)
        await this.saveSessionHistory(sessionData);
        
        // Clean up conversation data
        await this.cleanupSessionConversations(sessionId);
        
        // Remove from active sessions
        await this.removeActiveSession(sessionData.userId, sessionId);
        
        console.log(`Session ${sessionId} ended and cleaned up`);
    }

    /**
     * Save session history for analytics (short retention)
     */
    async saveSessionHistory(sessionData) {
        const historyKey = `session_history:${sessionData.sessionId}`;
        const historyData = {
            sessionId: sessionData.sessionId,
            userId: sessionData.userId,
            startTime: sessionData.startTime,
            endTime: sessionData.endTime,
            duration: sessionData.endTime - sessionData.startTime,
            conversationCount: sessionData.conversationCount,
            endReason: sessionData.endReason
        };
        
        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                // Keep session history for 24 hours for analytics
                await this.redisClient.setEx(historyKey, 86400, JSON.stringify(historyData));
            } catch (error) {
                console.log(`Redis save session history error: ${error.message}`);
            }
        }
    }

    /**
     * Remove session from active sessions list
     */
    async removeActiveSession(userId, sessionId) {
        const userSessionsKey = `user_sessions:${userId}`;
        const sessionKey = `session_data:${sessionId}`;
        
        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                await this.redisClient.sRem(userSessionsKey, sessionId);
                await this.redisClient.del(sessionKey);
            } catch (error) {
                console.log(`Redis remove session error: ${error.message}`);
            }
        }
        
        this.sessions.delete(sessionId);
    }

    /**
     * Clean up conversation data for a session
     */
    async cleanupSessionConversations(sessionId) {
        const conversationKey = `conversation:${sessionId}`;
        
        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                await this.redisClient.del(conversationKey);
                console.log(`Cleaned up conversations for session ${sessionId}`);
            } catch (error) {
                console.log(`Redis cleanup conversations error: ${error.message}`);
            }
        }
        
        this.store.delete(conversationKey);
    }

    /**
     * Start automatic cleanup timer
     */
    startCleanupTimer() {
        this.cleanupInterval = setInterval(async () => {
            await this.cleanupExpiredSessions();
        }, SESSION_CONFIG.CLEANUP_INTERVAL);
        
        console.log(`Started session cleanup timer (every ${SESSION_CONFIG.CLEANUP_INTERVAL/1000}s)`);
    }

    /**
     * Stop cleanup timer
     */
    stopCleanupTimer() {
        if (this.cleanupInterval) {
            clearInterval(this.cleanupInterval);
            this.cleanupInterval = null;
            console.log('Stopped session cleanup timer');
        }
    }

    /**
     * Clean up expired and inactive sessions
     */
    async cleanupExpiredSessions() {
        console.log('Running session cleanup...');
        
        try {
            if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
                // Get all session keys
                const sessionKeys = await this.redisClient.keys('session_data:*');
                let cleanedUp = 0;
                
                for (const sessionKey of sessionKeys) {
                    const sessionData = await this.redisClient.get(sessionKey);
                    if (!sessionData) continue;
                    
                    const session = JSON.parse(sessionData);
                    const now = Date.now();
                    const sessionAge = now - session.startTime;
                    const timeSinceActivity = now - session.lastActivity;
                    
                    // Check if session should be ended
                    if (sessionAge > SESSION_CONFIG.SESSION_DURATION * 1000 ||
                        timeSinceActivity > SESSION_CONFIG.INACTIVITY_TIMEOUT * 1000 ||
                        session.conversationCount >= SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION) {
                        
                        let reason = 'expired';
                        if (timeSinceActivity > SESSION_CONFIG.INACTIVITY_TIMEOUT * 1000) reason = 'inactive';
                        if (session.conversationCount >= SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION) reason = 'limit_reached';
                        
                        await this.endSession(session.sessionId, reason);
                        cleanedUp++;
                    }
                }
                
                if (cleanedUp > 0) {
                    console.log(`🗑️ Cleaned up ${cleanedUp} expired sessions`);
                }
            } else {
                // Fallback: cleanup memory sessions
                for (const [sessionId, sessionData] of this.sessions.entries()) {
                    const now = Date.now();
                    const sessionAge = now - sessionData.startTime;
                    const timeSinceActivity = now - sessionData.lastActivity;
                    
                    if (sessionAge > SESSION_CONFIG.SESSION_DURATION * 1000 ||
                        timeSinceActivity > SESSION_CONFIG.INACTIVITY_TIMEOUT * 1000 ||
                        sessionData.conversationCount >= SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION) {
                        
                        let reason = 'expired';
                        if (timeSinceActivity > SESSION_CONFIG.INACTIVITY_TIMEOUT * 1000) reason = 'inactive';
                        if (sessionData.conversationCount >= SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION) reason = 'limit_reached';
                        
                        await this.endSession(sessionId, reason);
                    }
                }
            }
        } catch (error) {
            console.log(`Session cleanup error: ${error.message}`);
        }
    }

    async initialize() {
        if (this.initialized) return;

        if (!this.useRedis) {
            console.log('Using in-memory session storage (Redis disabled)');
            this.initialized = true;
            return;
        }

        try {
            // Try to connect to Redis
            this.redisClient = createClient({
                url: process.env.REDIS_URL || 'redis://localhost:6379',
                socket: {
                    connectTimeout: 5000, // 5 seconds timeout
                    lazyConnect: true,
                    reconnectStrategy: (retries) => {
                        if (retries > 3) {
                            console.log('Redis connection failed after 3 retries, using in-memory storage');
                            return false;
                        }
                        return Math.min(retries * 50, 500);
                    }
                }
            });

            this.redisClient.on('error', (err) => {
                if (!this.redisConnected) {
                    console.log('Redis connection failed, falling back to in-memory storage');
                    this.redisClient = null;
                }
            });

            this.redisClient.on('connect', () => {
                console.log('Connected to Redis successfully');
                this.redisConnected = true;
            });

            this.redisClient.on('ready', () => {
                console.log('Redis client ready for commands');
            });

            this.redisClient.on('end', () => {
                console.log('Redis connection ended');
                this.redisConnected = false;
            });

            // Try to connect with timeout
            await Promise.race([
                this.redisClient.connect(),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Connection timeout')), 5000)
                )
            ]);
            
            // Test the connection
            await this.redisClient.ping();
            this.redisConnected = true;
            this.initialized = true;
            
        } catch (error) {
            console.log(`Failed to connect to Redis (${error.message}), using in-memory storage as fallback`);
            this.redisClient = null;
            this.redisConnected = false;
            this.initialized = true;
        }
    }

    async setMemory(key, value, ttl = 3600) {
        await this.initialize();

        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                await this.redisClient.setEx(key, ttl, JSON.stringify(value));
                return;
            } catch (error) {
                console.log(`Redis set error (${error.message}), falling back to memory`);
            }
        }
        
        // Use in-memory storage
        this.store.set(key, value);
        // Limit memory size for in-memory fallback
        if (this.store.size > SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION * 10) {
            const firstKey = this.store.keys().next().value;
            this.store.delete(firstKey);
        }
    }

    async getMemory(key) {
        await this.initialize();

        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                const value = await this.redisClient.get(key);
                return value ? JSON.parse(value) : null;
            } catch (error) {
                console.log(`Redis get error (${error.message}), falling back to memory`);
            }
        }
        
        // Use in-memory storage
        return this.store.get(key) || null;
    }

    async addToConversationHistory(userId, message, response) {
        await this.initialize();

        // Get or create session for user
        const sessionId = await this.getOrCreateSession(userId);
        const sessionData = await this.getSession(sessionId);
        
        if (!sessionData) {
            console.log(`No session data found for ${sessionId}`);
            return;
        }

        // Check if session has reached conversation limit
        if (sessionData.conversationCount >= SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION) {
            console.log(`⚠️ Session ${sessionId} has reached conversation limit, ending session`);
            await this.endSession(sessionId, 'limit_reached');
            // Create new session
            const newSessionId = await this.getOrCreateSession(userId);
            return this.addToConversationHistory(userId, message, response);
        }

        const conversationKey = `conversation:${sessionId}`;
        const timestamp = new Date().toISOString();
        
        const interaction = {
            timestamp,
            message,
            response,
            sessionId
        };

        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                // Get current conversation history for this session
                const historyData = await this.redisClient.get(conversationKey);
                let history = historyData ? JSON.parse(historyData) : [];
                
                // Add new interaction
                history.push(interaction);
                
                // Keep only recent interactions within session limit
                if (history.length > SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION) {
                    history = history.slice(-SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION);
                }
                
                // Save back to Redis with session TTL
                await this.redisClient.setEx(conversationKey, SESSION_CONFIG.SESSION_DURATION, JSON.stringify(history));
                
                // Update session data
                sessionData.conversationCount = history.length;
                sessionData.lastActivity = Date.now();
                await this.updateSession(sessionData);
                
                console.log(`Added conversation to session ${sessionId} (${sessionData.conversationCount}/${SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION})`);
                return;
            } catch (error) {
                console.log(`Redis conversation history error (${error.message}), using memory`);
            }
        }
        
        // Use in-memory storage
        let history = this.store.get(conversationKey) || [];
        history.push(interaction);
        
        if (history.length > SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION) {
            history = history.slice(-SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION);
        }
        
        this.store.set(conversationKey, history);
        
        // Update session data
        sessionData.conversationCount = history.length;
        sessionData.lastActivity = Date.now();
        await this.updateSession(sessionData);
    }

    async getConversationHistory(userId, limit = 10) {
        await this.initialize();

        // Get user's active session
        const sessions = await this.getUserActiveSessions(userId);
        if (sessions.length === 0) {
            return []; // No active sessions
        }
        
        // Get the most recent active session
        const mostRecentSession = sessions.sort((a, b) => b.lastActivity - a.lastActivity)[0];
        const conversationKey = `conversation:${mostRecentSession.sessionId}`;
        
        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                const historyData = await this.redisClient.get(conversationKey);
                const history = historyData ? JSON.parse(historyData) : [];
                return history.slice(-limit); // Return last N interactions from current session
            } catch (error) {
                console.log(`Redis get history error (${error.message}), using memory`);
            }
        }
        
        // Use in-memory storage
        const history = this.store.get(conversationKey) || [];
        return history.slice(-limit);
    }

    /**
     * Get conversation history for a specific session
     */
    async getSessionConversationHistory(sessionId, limit = 10) {
        await this.initialize();
        
        const conversationKey = `conversation:${sessionId}`;
        
        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                const historyData = await this.redisClient.get(conversationKey);
                const history = historyData ? JSON.parse(historyData) : [];
                return history.slice(-limit);
            } catch (error) {
                console.log(`Redis get session history error (${error.message}), using memory`);
            }
        }
        
        const history = this.store.get(conversationKey) || [];
        return history.slice(-limit);
    }

    /**
     * End user's current session manually
     */
    async endUserSession(userId, reason = 'manual') {
        const sessions = await this.getUserActiveSessions(userId);
        
        for (const session of sessions) {
            await this.endSession(session.sessionId, reason);
        }
        
        console.log(`Ended all sessions for user ${userId}`);
    }

    /**
     * Get session statistics
     */
    async getSessionStats(userId) {
        const sessions = await this.getUserActiveSessions(userId);
        const stats = {
            activeSessions: sessions.length,
            sessions: sessions.map(s => ({
                sessionId: s.sessionId,
                startTime: new Date(s.startTime).toISOString(),
                lastActivity: new Date(s.lastActivity).toISOString(),
                conversationCount: s.conversationCount,
                duration: Date.now() - s.startTime,
                status: s.status
            }))
        };
        
        return stats;
    }

    /**
     * Get system-wide memory usage stats
     */
    async getMemoryStats() {
        const stats = {
            sessionConfig: SESSION_CONFIG,
            timestamp: new Date().toISOString()
        };
        
        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                const sessionKeys = await this.redisClient.keys('session_data:*');
                const conversationKeys = await this.redisClient.keys('conversation:*');
                const historyKeys = await this.redisClient.keys('session_history:*');
                
                stats.redis = {
                    connected: true,
                    activeSessions: sessionKeys.length,
                    activeConversations: conversationKeys.length,
                    sessionHistories: historyKeys.length
                };
                
                // Get memory info from Redis
                const info = await this.redisClient.info('memory');
                const memoryMatch = info.match(/used_memory_human:([^\r\n]+)/);
                if (memoryMatch) {
                    stats.redis.memoryUsage = memoryMatch[1];
                }
            } catch (error) {
                console.log(`Redis stats error: ${error.message}`);
                stats.redis = { connected: false, error: error.message };
            }
        } else {
            stats.inMemory = {
                activeSessions: this.sessions.size,
                activeConversations: this.store.size
            };
        }
        
        return stats;
    }

    async disconnect() {
        // Stop cleanup timer
        this.stopCleanupTimer();
        
        // End all active sessions
        if (this.redisClient && this.redisConnected && this.redisClient.isOpen) {
            try {
                const sessionKeys = await this.redisClient.keys('session_data:*');
                for (const sessionKey of sessionKeys) {
                    const sessionData = await this.redisClient.get(sessionKey);
                    if (sessionData) {
                        const session = JSON.parse(sessionData);
                        if (session.status === 'active') {
                            await this.endSession(session.sessionId, 'shutdown');
                        }
                    }
                }
            } catch (error) {
                console.log('Error ending sessions during disconnect:', error.message);
            }
        }
        
        // Disconnect from Redis
        if (this.redisClient && this.redisClient.isOpen) {
            try {
                await this.redisClient.disconnect();
            } catch (error) {
                console.log('Error disconnecting from Redis:', error.message);
            }
        }
    }
}

// For backward compatibility
class MemoryStore extends SessionMemoryStore {
    constructor(useRedis = true) {
        console.log('⚠️ MemoryStore is deprecated, use SessionMemoryStore instead');
        super(useRedis);
    }
}

module.exports = {
    SessionMemoryStore,
    MemoryStore, // Backward compatibility
    SESSION_CONFIG
};
