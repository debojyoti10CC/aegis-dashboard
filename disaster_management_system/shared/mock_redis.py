"""
Mock Redis implementation for testing without Docker
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict, deque


class MockRedis:
    """Mock Redis implementation for testing"""
    
    def __init__(self):
        self.data = defaultdict(deque)
        self.logger = logging.getLogger("mock_redis")
        self.connected = False
    
    async def ping(self):
        """Mock ping"""
        return b'PONG'
    
    async def lpush(self, key: str, value: str):
        """Mock left push"""
        self.data[key].appendleft(value)
        return len(self.data[key])
    
    async def rpop(self, key: str):
        """Mock right pop"""
        if key in self.data and self.data[key]:
            return self.data[key].pop().encode()
        return None
    
    async def brpop(self, key: str, timeout: int = 1):
        """Mock blocking right pop"""
        # Simple non-blocking implementation for testing
        result = await self.rpop(key)
        if result:
            return (key.encode(), result)
        return None
    
    async def llen(self, key: str):
        """Mock list length"""
        return len(self.data.get(key, []))
    
    async def delete(self, key: str):
        """Mock delete"""
        if key in self.data:
            del self.data[key]
        return 1
    
    async def lrange(self, key: str, start: int, end: int):
        """Mock list range"""
        if key not in self.data:
            return []
        
        items = list(self.data[key])
        if end == -1:
            return [item.encode() for item in items[start:]]
        else:
            return [item.encode() for item in items[start:end+1]]
    
    async def keys(self, pattern: str):
        """Mock keys"""
        if pattern == "queue:*":
            return [key.encode() for key in self.data.keys() if key.startswith("queue:")]
        return []
    
    async def close(self):
        """Mock close"""
        self.connected = False


class MockMessageQueue:
    """Mock message queue using in-memory storage"""
    
    def __init__(self, redis_url: str = "mock://localhost"):
        self.redis_url = redis_url
        self.redis = MockRedis()
        self.logger = logging.getLogger("mock_message_queue")
        self.max_retries = 3
        self.retry_delay = 5
    
    async def connect(self):
        """Connect to mock Redis"""
        self.redis.connected = True
        self.logger.info("Connected to mock Redis message queue")
    
    async def disconnect(self):
        """Disconnect from mock Redis"""
        await self.redis.close()
        self.logger.info("Disconnected from mock Redis")
    
    async def publish(self, sender: str, recipient: str, payload: Dict[str, Any]):
        """Publish message to recipient's queue"""
        from .models import QueueMessage
        
        message = QueueMessage(
            message_id="",
            sender=sender,
            recipient=recipient,
            payload=payload,
            timestamp=datetime.utcnow()
        )
        
        queue_name = f"queue:{recipient}"
        
        try:
            await self.redis.lpush(queue_name, message.to_json())
            self.logger.info(f"Message sent from {sender} to {recipient}: {message.message_id}")
        except Exception as e:
            self.logger.error(f"Failed to publish message: {e}")
    
    async def consume(self, agent_name: str, timeout: int = 1) -> List:
        """Consume messages from agent's queue"""
        from .models import QueueMessage
        
        queue_name = f"queue:{agent_name}"
        messages = []
        
        try:
            result = await self.redis.brpop(queue_name, timeout=timeout)
            if result:
                _, message_data = result
                message = QueueMessage.from_json(message_data.decode())
                messages.append(message)
                self.logger.debug(f"Message consumed by {agent_name}: {message.message_id}")
        except Exception as e:
            self.logger.error(f"Failed to consume message for {agent_name}: {e}")
        
        return messages
    
    async def get_queue_size(self, agent_name: str) -> int:
        """Get the size of an agent's queue"""
        queue_name = f"queue:{agent_name}"
        try:
            return await self.redis.llen(queue_name)
        except Exception as e:
            self.logger.error(f"Failed to get queue size for {agent_name}: {e}")
            return 0
    
    async def clear_queue(self, agent_name: str):
        """Clear all messages from an agent's queue"""
        queue_name = f"queue:{agent_name}"
        try:
            await self.redis.delete(queue_name)
            self.logger.info(f"Cleared queue for {agent_name}")
        except Exception as e:
            self.logger.error(f"Failed to clear queue for {agent_name}: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check mock Redis connection health"""
        try:
            await self.redis.ping()
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_all_queue_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all queues"""
        stats = {}
        
        try:
            queue_keys = await self.redis.keys("queue:*")
            
            for key in queue_keys:
                key_str = key.decode()
                if ':dlq' not in key_str:
                    agent_name = key_str.replace('queue:', '')
                    queue_size = await self.redis.llen(key)
                    
                    stats[agent_name] = {
                        'queue_size': queue_size,
                        'dlq_size': 0,  # Mock DLQ
                        'last_updated': datetime.utcnow().isoformat()
                    }
        except Exception as e:
            self.logger.error(f"Failed to get queue stats: {e}")
        
        return stats