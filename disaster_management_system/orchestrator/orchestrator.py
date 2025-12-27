"""
Agent Orchestrator - Manages lifecycle and coordination of all agents
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import yaml
import os
from dotenv import load_dotenv

from ..shared.message_queue import MessageQueue
from ..shared.models import AgentStatus
from ..agents.watchtower import WatchtowerAgent
from ..agents.auditor import AuditorAgent
from ..agents.treasurer import TreasurerAgent


class AgentOrchestrator:
    """Orchestrates all disaster management agents"""
    
    def __init__(self, config_path: str = "config.yaml"):
        # Load environment variables from .env file
        load_dotenv()
        
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger("orchestrator")
        
        # Agent management
        self.agents = {}
        self.agent_tasks = {}
        self.agent_status = {}
        
        # Message queue
        self.message_queue = None
        
        # Monitoring
        self.last_heartbeat = {}
        self.restart_counts = {}
        self.max_restarts = self.config.get('max_restarts', 5)
        self.heartbeat_timeout = self.config.get('heartbeat_timeout', 60)  # seconds
        
        # System state
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                # Return default configuration
                return self._get_default_config()
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'redis': {
                'url': 'redis://localhost:6379'
            },
            'agents': {
                'watchtower': {
                    'enabled': True,
                    'heartbeat_interval': 30
                },
                'auditor': {
                    'enabled': True,
                    'heartbeat_interval': 30
                },
                'treasurer': {
                    'enabled': True,
                    'heartbeat_interval': 30,
                    'blockchain': {
                        'network_url': 'https://sepolia.infura.io/v3/YOUR_PROJECT_ID',
                        'private_key': '',
                        'gas_limit': 21000,
                        'gas_price': 20000000000
                    }
                }
            },
            'monitoring': {
                'heartbeat_timeout': 60,
                'max_restarts': 5,
                'health_check_interval': 30
            }
        }
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start the orchestrator and all agents"""
        try:
            self.logger.info("Starting Disaster Management System Orchestrator")
            self.is_running = True
            
            # Initialize message queue
            redis_config = self.config.get('redis', {})
            self.message_queue = MessageQueue(redis_config.get('url', 'redis://localhost:6379'))
            await self.message_queue.connect()
            
            # Start agents
            await self._start_agents()
            
            # Start monitoring tasks
            monitoring_task = asyncio.create_task(self._monitoring_loop())
            health_check_task = asyncio.create_task(self._health_check_loop())
            
            self.logger.info("All systems started successfully")
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
            # Cancel monitoring tasks
            monitoring_task.cancel()
            health_check_task.cancel()
            
            # Stop all agents
            await self._stop_agents()
            
            # Disconnect message queue
            await self.message_queue.disconnect()
            
            self.logger.info("Orchestrator shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error in orchestrator: {e}")
            await self.shutdown()
    
    async def _start_agents(self):
        """Start all configured agents"""
        agent_configs = self.config.get('agents', {})
        
        for agent_name, agent_config in agent_configs.items():
            if not agent_config.get('enabled', True):
                self.logger.info(f"Agent {agent_name} is disabled, skipping")
                continue
            
            try:
                await self._start_agent(agent_name, agent_config)
            except Exception as e:
                self.logger.error(f"Failed to start agent {agent_name}: {e}")
    
    async def _start_agent(self, agent_name: str, agent_config: Dict[str, Any]):
        """Start a specific agent"""
        try:
            # Create agent instance
            if agent_name == 'watchtower':
                agent = WatchtowerAgent(agent_config)
            elif agent_name == 'auditor':
                agent = AuditorAgent(agent_config)
            elif agent_name == 'treasurer':
                agent = TreasurerAgent(agent_config)
            else:
                self.logger.error(f"Unknown agent type: {agent_name}")
                return
            
            # Set message queue
            agent.set_message_queue(self.message_queue)
            
            # Start agent in background task
            agent_task = asyncio.create_task(agent.start())
            
            # Store references
            self.agents[agent_name] = agent
            self.agent_tasks[agent_name] = agent_task
            self.restart_counts[agent_name] = 0
            self.last_heartbeat[agent_name] = datetime.utcnow()
            
            # Initialize status
            self.agent_status[agent_name] = AgentStatus(
                agent_name=agent_name,
                status='running',
                last_heartbeat=datetime.utcnow(),
                processed_count=0,
                error_count=0
            )
            
            self.logger.info(f"Agent {agent_name} started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting agent {agent_name}: {e}")
            raise
    
    async def _stop_agents(self):
        """Stop all agents"""
        for agent_name, agent in self.agents.items():
            try:
                await agent.stop()
                
                # Cancel agent task
                if agent_name in self.agent_tasks:
                    self.agent_tasks[agent_name].cancel()
                
                self.logger.info(f"Agent {agent_name} stopped")
                
            except Exception as e:
                self.logger.error(f"Error stopping agent {agent_name}: {e}")
    
    async def _monitoring_loop(self):
        """Monitor agent health and restart failed agents"""
        while self.is_running:
            try:
                await self._check_agent_health()
                await asyncio.sleep(self.config.get('monitoring', {}).get('health_check_interval', 30))
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _health_check_loop(self):
        """Perform periodic health checks"""
        while self.is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(60)  # Health check every minute
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(30)
    
    async def _check_agent_health(self):
        """Check health of all agents"""
        current_time = datetime.utcnow()
        
        for agent_name, agent in self.agents.items():
            try:
                # Check if agent task is still running
                agent_task = self.agent_tasks.get(agent_name)
                if agent_task and agent_task.done():
                    self.logger.warning(f"Agent {agent_name} task has finished unexpectedly")
                    await self._restart_agent(agent_name)
                    continue
                
                # Check heartbeat timeout
                last_heartbeat = self.last_heartbeat.get(agent_name, current_time)
                time_since_heartbeat = (current_time - last_heartbeat).total_seconds()
                
                if time_since_heartbeat > self.heartbeat_timeout:
                    self.logger.warning(f"Agent {agent_name} heartbeat timeout ({time_since_heartbeat}s)")
                    await self._restart_agent(agent_name)
                    continue
                
                # Update status
                if agent_name in self.agent_status:
                    self.agent_status[agent_name].status = 'running'
                    self.agent_status[agent_name].last_heartbeat = last_heartbeat
                
            except Exception as e:
                self.logger.error(f"Error checking health of agent {agent_name}: {e}")
    
    async def _restart_agent(self, agent_name: str):
        """Restart a failed agent"""
        try:
            # Check restart limit
            restart_count = self.restart_counts.get(agent_name, 0)
            if restart_count >= self.max_restarts:
                self.logger.error(f"Agent {agent_name} exceeded max restarts ({self.max_restarts})")
                self.agent_status[agent_name].status = 'failed'
                return
            
            self.logger.info(f"Restarting agent {agent_name} (attempt {restart_count + 1})")
            
            # Stop existing agent
            if agent_name in self.agents:
                await self.agents[agent_name].stop()
            
            if agent_name in self.agent_tasks:
                self.agent_tasks[agent_name].cancel()
            
            # Wait a bit before restart
            await asyncio.sleep(5)
            
            # Start agent again
            agent_config = self.config.get('agents', {}).get(agent_name, {})
            await self._start_agent(agent_name, agent_config)
            
            # Update restart count
            self.restart_counts[agent_name] = restart_count + 1
            
            self.logger.info(f"Agent {agent_name} restarted successfully")
            
        except Exception as e:
            self.logger.error(f"Error restarting agent {agent_name}: {e}")
            if agent_name in self.agent_status:
                self.agent_status[agent_name].status = 'error'
    
    async def _perform_health_checks(self):
        """Perform comprehensive health checks"""
        try:
            # Check message queue health
            if self.message_queue:
                health = await self.message_queue.health_check()
                if health['status'] != 'healthy':
                    self.logger.warning(f"Message queue unhealthy: {health}")
            
            # Check queue sizes
            if self.message_queue:
                queue_stats = await self.message_queue.get_all_queue_stats()
                for agent_name, stats in queue_stats.items():
                    if stats['queue_size'] > 100:  # Alert if queue is backing up
                        self.logger.warning(f"Agent {agent_name} queue size: {stats['queue_size']}")
                    
                    if stats['dlq_size'] > 0:  # Alert if there are failed messages
                        self.logger.warning(f"Agent {agent_name} DLQ size: {stats['dlq_size']}")
            
        except Exception as e:
            self.logger.error(f"Error in health checks: {e}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Initiating graceful shutdown...")
        self.is_running = False
        self.shutdown_event.set()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            agent_statuses = {}
            for agent_name, status in self.agent_status.items():
                agent_statuses[agent_name] = {
                    'status': status.status,
                    'last_heartbeat': status.last_heartbeat.isoformat(),
                    'processed_count': status.processed_count,
                    'error_count': status.error_count,
                    'restart_count': self.restart_counts.get(agent_name, 0)
                }
            
            return {
                'orchestrator_status': 'running' if self.is_running else 'stopped',
                'agents': agent_statuses,
                'message_queue_connected': self.message_queue is not None,
                'total_agents': len(self.agents),
                'running_agents': sum(1 for s in self.agent_status.values() if s.status == 'running'),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    async def inject_test_event(self, image_path: str, coordinates: tuple = None):
        """Inject a test disaster event (for testing purposes)"""
        try:
            if 'watchtower' not in self.agents:
                return {'error': 'Watchtower agent not available'}
            
            watchtower = self.agents['watchtower']
            result = await watchtower.process_test_image(image_path, coordinates)
            
            return {
                'status': 'test_event_injected',
                'result': result.to_dict() if result else None
            }
            
        except Exception as e:
            self.logger.error(f"Error injecting test event: {e}")
            return {'error': str(e)}
    
    async def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get statistics for a specific agent"""
        try:
            if agent_name not in self.agents:
                return {'error': f'Agent {agent_name} not found'}
            
            agent = self.agents[agent_name]
            
            # Get agent-specific stats
            if hasattr(agent, 'get_verification_stats') and agent_name == 'auditor':
                return await agent.get_verification_stats()
            elif hasattr(agent, 'get_funding_stats') and agent_name == 'treasurer':
                return await agent.get_funding_stats()
            else:
                # Return basic stats
                status = self.agent_status.get(agent_name)
                return {
                    'agent_name': agent_name,
                    'status': status.status if status else 'unknown',
                    'restart_count': self.restart_counts.get(agent_name, 0),
                    'last_heartbeat': status.last_heartbeat.isoformat() if status else None
                }
                
        except Exception as e:
            self.logger.error(f"Error getting agent stats: {e}")
            return {'error': str(e)}