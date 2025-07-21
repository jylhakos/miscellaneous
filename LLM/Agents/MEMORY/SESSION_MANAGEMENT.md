# Session Management

## Overview

The LangChain Weather Agent implements session-based memory management to limit Redis memory usage and provide better conversation context management. Each user's conversations are organized into sessions with automatic cleanup.

## Session concept

A **session** is defined as:
- A time-bounded conversation period for a user
- Limited number of conversations per session
- Automatic cleanup after inactivity or expiration
- Isolated memory space that gets cleaned up when session ends

## Session configuration

Session behavior is controlled by environment variables in `.env`:

```bash
# Session duration in seconds (default: 1800 = 30 minutes)
SESSION_DURATION=1800

# Maximum conversations per session (default: 20)
MAX_CONVERSATIONS_PER_SESSION=20

# Inactivity timeout in seconds (default: 900 = 15 minutes)
INACTIVITY_TIMEOUT=900

# Cleanup interval in milliseconds (default: 300000 = 5 minutes)
CLEANUP_INTERVAL=300000
```

## Session lifecycle

### 1. Session Creation
- Automatically created when user sends first message
- Session ID format: `session:userId:timestamp`
- Stored in Redis with TTL

### 2. Session Activity
- Each message updates `lastActivity` timestamp
- Conversation counter increments
- Session data saved to Redis with TTL refresh

### 3. Session Termination
Sessions end when:
- **Time Limit**: Session duration exceeded
- **Inactivity**: No activity for inactivity timeout period
- **Conversation Limit**: Maximum conversations per session reached
- **Manual**: Explicitly ended via API call
- **Shutdown**: Application shutdown

### 4. Session Cleanup
When a session ends:
- All conversation data is deleted from Redis
- Session marked as 'ended' in history (brief retention)
- User session list updated
- Memory freed immediately

## Memory

### Before (Traditional)
- Unlimited conversation history per user
- Memory grows indefinitely
- No automatic cleanup
- Redis memory usage increases over time

### After (Session-based)
- Limited conversations per session (default: 20)
- Automatic cleanup after session ends
- Memory usage bounded and predictable
- Redis memory freed regularly

## API Endpoints

### Session Information
```bash
# Get user's active sessions
GET /sessions/:userId

# Get session conversation history
GET /sessions/:userId/history
GET /sessions/:userId/history/:sessionId

# End user's sessions
POST /sessions/:userId/end
```

### System Monitoring
```bash
# Memory usage statistics  
GET /system/memory

# Complete system status
GET /system/status
```

## Usage

### 1. Start application with Session Management
```bash
npm run system:start
# or
./process-manager.sh start
```

### 2. Test Session Management
```bash
npm run session-demo
# or
node session-demo.js
```

### 3. Monitor Memory usage
```bash
# Check memory stats
curl http://localhost:3000/system/memory

# Check user sessions
curl http://localhost:3000/sessions/user123

# End user sessions
curl -X POST http://localhost:3000/sessions/user123/end \
  -H "Content-Type: application/json" \
  -d '{"reason": "user_requested"}'
```

### 4. Chat with Session Tracking
```bash
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "userId": "user123"}'
  
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Weather in London?", "userId": "user123"}'
```

## Session monitoring

### Real-time monitoring
```bash
# Live system monitoring
npm run system:monitor
# or
./process-manager.sh monitor
```

### Session Statistics
The system provides detailed session statistics:
- Active sessions per user
- Conversation counts
- Session durations
- Memory usage
- Cleanup statistics

## Configurations

### Development
```bash
SESSION_DURATION=900        # 15 minutes
MAX_CONVERSATIONS_PER_SESSION=10
INACTIVITY_TIMEOUT=300      # 5 minutes
CLEANUP_INTERVAL=60000      # 1 minute
```

### Production
```bash
SESSION_DURATION=3600       # 1 hour
MAX_CONVERSATIONS_PER_SESSION=50
INACTIVITY_TIMEOUT=1800     # 30 minutes
CLEANUP_INTERVAL=300000     # 5 minutes
```

### Memory-Constrained environment
```bash
SESSION_DURATION=600        # 10 minutes
MAX_CONVERSATIONS_PER_SESSION=5
INACTIVITY_TIMEOUT=180      # 3 minutes
CLEANUP_INTERVAL=30000      # 30 seconds
```

## Backward compatibility

The system maintains backward compatibility:
- Old `MemoryStore` class still available (deprecated)
- Existing API endpoints continue to work
- Gradual migration path provided

## Summary

1. **Memory Efficiency**: Bounded memory usage with automatic cleanup
2. **Predictable Performance**: Known memory limits prevent Redis bloat
3. **Better UX**: Session-based conversations feel more natural
4. **Automatic Management**: No manual cleanup required
5. **Monitoring**: Comprehensive stats and monitoring
6. **Configurable**: Flexible session parameters for different use cases
7. **Reliable**: Graceful fallback to in-memory storage if Redis fails

## Troubleshooting

### High Memory Usage
1. Check session configuration - reduce limits if needed
2. Monitor cleanup interval - increase frequency if needed
3. Check for stuck sessions - manually end if required

### Sessions Not Cleaning Up
1. Verify cleanup timer is running (check logs)
2. Check Redis connectivity
3. Manually trigger cleanup via API

### Performance Issues
1. Reduce MAX_CONVERSATIONS_PER_SESSION
2. Decrease SESSION_DURATION
3. Increase CLEANUP_INTERVAL for less frequent cleanup

### Redis Connection Issues
1. System automatically falls back to in-memory storage
2. Session management still works with in-memory fallback
3. Check Redis container status and connectivity
