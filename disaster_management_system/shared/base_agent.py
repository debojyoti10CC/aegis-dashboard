"""
Base agent class for all disaster management agents
"""

import asyncio
import logging
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseAgent(ABC):
    """Base class for all agents in the disaster management system"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"agent.{name}")
        self.is_running = False
        self.message_queue = None
        self.heartbeat_interval = config.get('heartbeat_interval', 30)
        
    async def start(self):
        """Start the agent"""
        self.logger.info(f"Starting {self.name} agent")
        self.is_running = True
        
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Start main processing loop
        processing_task = asyncio.create_task(self._processing_loop())
        
        # Wait for both tasks
        await asyncio.gather(heartbeat_task, processing_task)
    
    async def stop(self):
        """Stop the agent"""
        self.logger.info(f"Stopping {self.name} agent")
        self.is_running = False
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat signals"""
        while self.is_running:
            await self._send_heartbeat()
            await asyncio.sleep(self.heartbeat_interval)
    
    async def _send_heartbeat(self):
        """Send heartbeat to orchestrator"""
        heartbeat_data = {
            'agent_name': self.name,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'running' if self.is_running else 'stopped'
        }
        self.logger.debug(f"Heartbeat: {heartbeat_data}")
    
    @abstractmethod
    async def _processing_loop(self):
        """Main processing loop - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming message - to be implemented by subclasses"""
        pass
    
    def set_message_queue(self, message_queue):
        """Set the message queue for inter-agent communication"""
        self.message_queue = message_queue
    
    async def send_message(self, recipient: str, payload: Dict[str, Any]):
        """Send message to another agent"""
        if self.message_queue:
            await self.message_queue.publish(
                sender=self.name,
                recipient=recipient,
                payload=payload
            )
        else:
            self.logger.error("Message queue not set")
    
    async def receive_messages(self):
        """Receive messages from the queue"""
        if self.message_queue:
            return await self.message_queue.consume(self.name)
        return []