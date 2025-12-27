"""
Redis-based message queue system for inter-agent communication
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from .models import QueueMessage

# Try to import aioredis, fall back to mock if not available
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import aioredis
        REDIS_AVAILABLE = True
    except ImportError:
        REDIS_AVAILABLE = False


class MessageQueue:
    """Redis-based message queue for agent communication"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.logger = logging.getLogger("message_queue")
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.use_mock = False
    
    async def connect(self):
        """Connect to Redis"""
        if not REDIS_AVAILABLE:
            self.logger.warning("Redis not available, using mock implementation")
            await self._use_mock()
            return
            
        try:
            if hasattr(aioredis, 'from_url'):
                self.redis = await aioredis.from_url(self.redis_url)
            else:
                self.redis = aioredis.Redis.from_url(self.redis_url)
            
            await self.redis.ping()
            self.logger.info("Connected to Redis message queue")
        except Exception as e:
            self.logger.warning(f"Failed to connect to Redis: {e}")
            self.logger.info("Falling back to mock Redis for testing")
            await self._use_mock()
    
    async def _use_mock(self):
        """Use mock Redis implementation"""
        from .mock_redis import MockMessageQueue
        mock_queue = MockMessageQueue()
        await mock_queue.connect()
        
        # Replace this instance with mock
        self.__dict__.update(mock_queue.__dict__)
        self.use_mock = True
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis and not self.use_mock:
            await self.redis.close()
            self.logger.info("Disconnected from Redis")
    
    async def publish(self, sender: str, recipient: str, payload: Dict[str, Any]):
        """Publish message to recipient's queue"""
        if self.use_mock:
            # This will be handled by mock implementation
            return
            
        message = QueueMessage(
            message_id="",  # Will be auto-generated
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
            # Store in dead letter queue
            await self._store_in_dlq(message, str(e))
    
    async def consume(self, agent_name: str, timeout: int = 1) -> List[QueueMessage]:
        """Consume messages from agent's queue"""
        if self.use_mock:
            # This will be handled by mock implementation
            return []
            
        queue_name = f"queue:{agent_name}"
        messages = []
        
        try:
            # Use BRPOP for blocking pop with timeout
            result = await self.redis.brpop(queue_name, timeout=timeout)
            if result:
                _, message_data = result
                message = QueueMessage.from_json(message_data.decode())
                messages.append(message)
                self.logger.debug(f"Message consumed by {agent_name}: {message.message_id}")
        except Exception as e:
            self.logger.error(f"Failed to consume message for {agent_name}: {e}")
        
        return messages
    
    async def consume_batch(self, agent_name: str, batch_size: int = 10) -> List[QueueMessage]:
        """Consume multiple messages at once"""
        queue_name = f"queue:{agent_name}"
        messages = []
        
        try:
            for _ in range(batch_size):
                result = await self.redis.rpop(queue_name)
                if not result:
                    break
                
                message = QueueMessage.from_json(result.decode())
                messages.append(message)
            
            if messages:
                self.logger.info(f"Batch consumed {len(messages)} messages for {agent_name}")
        except Exception as e:
            self.logger.error(f"Failed to consume batch for {agent_name}: {e}")
        
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
    
    async def _store_in_dlq(self, message: QueueMessage, error: str):
        """Store failed message in dead letter queue"""
        dlq_name = f"queue:{message.recipient}:dlq"
        dlq_data = {
            'message': message.to_json(),
            'error': error,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            await self.redis.lpush(dlq_name, json.dumps(dlq_data))
            self.logger.warning(f"Message stored in DLQ: {message.message_id}")
        except Exception as e:
            self.logger.error(f"Failed to store message in DLQ: {e}")
    
    async def get_dlq_messages(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get messages from dead letter queue"""
        dlq_name = f"queue:{agent_name}:dlq"
        messages = []
        
        try:
            dlq_messages = await self.redis.lrange(dlq_name, 0, -1)
            for msg_data in dlq_messages:
                messages.append(json.loads(msg_data.decode()))
        except Exception as e:
            self.logger.error(f"Failed to get DLQ messages for {agent_name}: {e}")
        
        return messages
    
    async def retry_message(self, message: QueueMessage) -> bool:
        """Retry a failed message"""
        if message.retry_count >= self.max_retries:
            self.logger.warning(f"Message {message.message_id} exceeded max retries")
            return False
        
        message.retry_count += 1
        
        # Wait before retry
        await asyncio.sleep(self.retry_delay * message.retry_count)
        
        # Republish message
        await self.publish(message.sender, message.recipient, message.payload)
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health"""
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
            # Get all queue keys
            queue_keys = await self.redis.keys("queue:*")
            
            for key in queue_keys:
                key_str = key.decode()
                if ':dlq' not in key_str:
                    agent_name = key_str.replace('queue:', '')
                    queue_size = await self.redis.llen(key)
                    dlq_size = await self.redis.llen(f"{key_str}:dlq")
                    
                    stats[agent_name] = {
                        'queue_size': queue_size,
                        'dlq_size': dlq_size,
                        'last_updated': datetime.utcnow().isoformat()
                    }
        except Exception as e:
            self.logger.error(f"Failed to get queue stats: {e}")
        
        return stats