#!/usr/bin/env python3
"""
Disaster Management System CLI
Command-line interface for controlling and monitoring the system
"""

import asyncio
import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from disaster_management_system.orchestrator.orchestrator import AgentOrchestrator
from disaster_management_system.shared.logging_config import setup_logging
from disaster_management_system.shared.message_queue import MessageQueue
from disaster_management_system.shared.models import ImageInput


class DisasterCLI:
    """Command-line interface for the disaster management system"""
    
    def __init__(self):
        self.orchestrator = None
        self.message_queue = None
    
    async def start_system(self, config_path: str = "config.yaml"):
        """Start the entire disaster management system"""
        try:
            print("🚀 Starting Disaster Management System...")
            
            # Setup logging
            setup_logging()
            
            # Create and start orchestrator
            self.orchestrator = AgentOrchestrator(config_path)
            
            print("✅ System started successfully!")
            print("📊 Use 'python -m disaster_management_system.cli.main status' to monitor")
            print("🛑 Press Ctrl+C to stop the system")
            
            # Start orchestrator (this will block)
            await self.orchestrator.start()
            
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
        except Exception as e:
            print(f"❌ Error starting system: {e}")
            return 1
        
        return 0
    
    async def stop_system(self):
        """Stop the disaster management system"""
        try:
            print("🛑 Stopping Disaster Management System...")
            
            if self.orchestrator:
                await self.orchestrator.shutdown()
            
            print("✅ System stopped successfully!")
            
        except Exception as e:
            print(f"❌ Error stopping system: {e}")
            return 1
        
        return 0
    
    async def get_status(self, config_path: str = "config.yaml"):
        """Get system status"""
        try:
            # Connect to message queue to check system health
            from disaster_management_system.shared.logging_config import get_default_logging_config
            import yaml
            
            # Load config
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                print(f"❌ Config file not found: {config_path}")
                return 1
            
            # Connect to Redis
            redis_url = config.get('redis', {}).get('url', 'redis://localhost:6379')
            message_queue = MessageQueue(redis_url)
            
            try:
                await message_queue.connect()
                
                # Get queue statistics
                queue_stats = await message_queue.get_all_queue_stats()
                health = await message_queue.health_check()
                
                print("📊 Disaster Management System Status")
                print("=" * 50)
                print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"🔗 Redis Status: {health['status']}")
                print()
                
                if queue_stats:
                    print("📬 Agent Queue Status:")
                    for agent_name, stats in queue_stats.items():
                        status_icon = "✅" if stats['queue_size'] < 10 else "⚠️" if stats['queue_size'] < 50 else "❌"
                        print(f"  {status_icon} {agent_name.capitalize()}: {stats['queue_size']} messages, {stats['dlq_size']} failed")
                else:
                    print("📬 No agent queues found (system may not be running)")
                
                await message_queue.disconnect()
                
            except Exception as e:
                print(f"❌ Cannot connect to Redis: {e}")
                print("💡 Make sure the system is running with 'python -m disaster_management_system.cli.main start'")
                return 1
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return 1
        
        return 0
    
    async def inject_test_event(self, image_path: str, coordinates: str = None):
        """Inject a test disaster event"""
        try:
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return 1
            
            print(f"🧪 Injecting test event with image: {image_path}")
            
            # Parse coordinates if provided
            coords = None
            if coordinates:
                try:
                    lat, lon = map(float, coordinates.split(','))
                    coords = (lat, lon)
                except ValueError:
                    print("❌ Invalid coordinates format. Use: lat,lon (e.g., 37.7749,-122.4194)")
                    return 1
            
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Create image input
            image_input = ImageInput(
                image_data=image_data,
                timestamp=datetime.utcnow(),
                coordinates=coords,
                source_type="test",
                metadata={'test_injection': True, 'file_path': image_path}
            )
            
            # Connect to message queue and send to watchtower
            from disaster_management_system.shared.logging_config import get_default_logging_config
            import yaml
            
            # Load config
            config_path = "config.yaml"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                config = {'redis': {'url': 'redis://localhost:6379'}}
            
            redis_url = config.get('redis', {}).get('url', 'redis://localhost:6379')
            message_queue = MessageQueue(redis_url)
            
            await message_queue.connect()
            
            # Send message to watchtower
            await message_queue.publish(
                sender="cli",
                recipient="watchtower",
                payload={'image_input': image_input.to_dict()}
            )
            
            await message_queue.disconnect()
            
            print("✅ Test event injected successfully!")
            print("📊 Monitor the system with 'python -m disaster_management_system.cli.main status'")
            
        except Exception as e:
            print(f"❌ Error injecting test event: {e}")
            return 1
        
        return 0
    
    async def view_logs(self, agent: str = None, lines: int = 50):
        """View system logs"""
        try:
            log_dir = "logs"
            
            if not os.path.exists(log_dir):
                print(f"❌ Log directory not found: {log_dir}")
                return 1
            
            if agent:
                log_file = os.path.join(log_dir, f"{agent}.log")
                if not os.path.exists(log_file):
                    print(f"❌ Log file not found: {log_file}")
                    return 1
                
                print(f"📋 Last {lines} lines from {agent} agent:")
                print("=" * 50)
                
                with open(log_file, 'r') as f:
                    log_lines = f.readlines()
                    for line in log_lines[-lines:]:
                        try:
                            # Try to parse as JSON for pretty printing
                            log_entry = json.loads(line.strip())
                            timestamp = log_entry.get('timestamp', '')
                            level = log_entry.get('level', '')
                            message = log_entry.get('message', '')
                            print(f"{timestamp} [{level}] {message}")
                        except json.JSONDecodeError:
                            # Fallback to raw line
                            print(line.strip())
            else:
                # Show main system log
                log_file = os.path.join(log_dir, "disaster_system.log")
                if os.path.exists(log_file):
                    print(f"📋 Last {lines} lines from system log:")
                    print("=" * 50)
                    
                    with open(log_file, 'r') as f:
                        log_lines = f.readlines()
                        for line in log_lines[-lines:]:
                            try:
                                log_entry = json.loads(line.strip())
                                timestamp = log_entry.get('timestamp', '')
                                level = log_entry.get('level', '')
                                logger = log_entry.get('logger', '')
                                message = log_entry.get('message', '')
                                print(f"{timestamp} [{level}] {logger}: {message}")
                            except json.JSONDecodeError:
                                print(line.strip())
                else:
                    print("📋 Available log files:")
                    for file in os.listdir(log_dir):
                        if file.endswith('.log'):
                            print(f"  - {file}")
            
        except Exception as e:
            print(f"❌ Error viewing logs: {e}")
            return 1
        
        return 0
    
    async def clear_queues(self):
        """Clear all message queues"""
        try:
            print("🧹 Clearing all message queues...")
            
            # Load config
            config_path = "config.yaml"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                config = {'redis': {'url': 'redis://localhost:6379'}}
            
            redis_url = config.get('redis', {}).get('url', 'redis://localhost:6379')
            message_queue = MessageQueue(redis_url)
            
            await message_queue.connect()
            
            # Clear queues for all agents
            agents = ['watchtower', 'auditor', 'treasurer']
            for agent in agents:
                await message_queue.clear_queue(agent)
                print(f"✅ Cleared {agent} queue")
            
            await message_queue.disconnect()
            
            print("✅ All queues cleared successfully!")
            
        except Exception as e:
            print(f"❌ Error clearing queues: {e}")
            return 1
        
        return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Disaster Management System CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the disaster management system')
    start_parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    
    # Stop command
    subparsers.add_parser('stop', help='Stop the disaster management system')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get system status')
    status_parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Inject test disaster event')
    test_parser.add_argument('image', help='Path to test image file')
    test_parser.add_argument('--coordinates', help='GPS coordinates (lat,lon)')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='View system logs')
    logs_parser.add_argument('--agent', choices=['watchtower', 'auditor', 'treasurer', 'orchestrator'], 
                           help='Specific agent logs to view')
    logs_parser.add_argument('--lines', type=int, default=50, help='Number of lines to show')
    
    # Clear command
    subparsers.add_parser('clear', help='Clear all message queues')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = DisasterCLI()
    
    try:
        if args.command == 'start':
            return asyncio.run(cli.start_system(args.config))
        elif args.command == 'stop':
            return asyncio.run(cli.stop_system())
        elif args.command == 'status':
            return asyncio.run(cli.get_status(args.config))
        elif args.command == 'test':
            return asyncio.run(cli.inject_test_event(args.image, args.coordinates))
        elif args.command == 'logs':
            return asyncio.run(cli.view_logs(args.agent, args.lines))
        elif args.command == 'clear':
            return asyncio.run(cli.clear_queues())
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())