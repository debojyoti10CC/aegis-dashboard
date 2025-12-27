"""
Logging configuration for the disaster management system
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Dict, Any


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


def setup_logging(config: Dict[str, Any] = None):
    """Setup logging configuration for the entire system"""
    
    if config is None:
        config = get_default_logging_config()
    
    # Create logs directory if it doesn't exist
    log_dir = config.get('log_dir', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.get('level', 'INFO')))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if config.get('console', {}).get('enabled', True):
        console_handler = logging.StreamHandler()
        console_level = config.get('console', {}).get('level', 'INFO')
        console_handler.setLevel(getattr(logging, console_level))
        
        if config.get('console', {}).get('json_format', False):
            console_handler.setFormatter(JSONFormatter())
        else:
            console_format = config.get('console', {}).get('format', 
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(logging.Formatter(console_format))
        
        root_logger.addHandler(console_handler)
    
    # File handler
    if config.get('file', {}).get('enabled', True):
        file_path = os.path.join(log_dir, config.get('file', {}).get('filename', 'disaster_system.log'))
        
        # Use rotating file handler
        max_bytes = config.get('file', {}).get('max_bytes', 10 * 1024 * 1024)  # 10MB
        backup_count = config.get('file', {}).get('backup_count', 5)
        
        file_handler = logging.handlers.RotatingFileHandler(
            file_path, maxBytes=max_bytes, backupCount=backup_count
        )
        
        file_level = config.get('file', {}).get('level', 'DEBUG')
        file_handler.setLevel(getattr(logging, file_level))
        
        if config.get('file', {}).get('json_format', True):
            file_handler.setFormatter(JSONFormatter())
        else:
            file_format = config.get('file', {}).get('format',
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(logging.Formatter(file_format))
        
        root_logger.addHandler(file_handler)
    
    # Agent-specific log files
    if config.get('agent_files', {}).get('enabled', True):
        for agent_name in ['watchtower', 'auditor', 'treasurer', 'orchestrator']:
            agent_logger = logging.getLogger(f"agent.{agent_name}")
            
            agent_file_path = os.path.join(log_dir, f"{agent_name}.log")
            agent_handler = logging.handlers.RotatingFileHandler(
                agent_file_path, maxBytes=5 * 1024 * 1024, backupCount=3  # 5MB
            )
            
            agent_handler.setLevel(logging.DEBUG)
            agent_handler.setFormatter(JSONFormatter())
            agent_logger.addHandler(agent_handler)
    
    logging.info("Logging system initialized")


def get_default_logging_config() -> Dict[str, Any]:
    """Get default logging configuration"""
    return {
        'level': 'INFO',
        'log_dir': 'logs',
        'console': {
            'enabled': True,
            'level': 'INFO',
            'json_format': False,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'file': {
            'enabled': True,
            'level': 'DEBUG',
            'filename': 'disaster_system.log',
            'json_format': True,
            'max_bytes': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5
        },
        'agent_files': {
            'enabled': True
        }
    }


class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)
    
    def log_processing_time(self, agent_name: str, operation: str, 
                          processing_time: float, success: bool = True, **kwargs):
        """Log processing time metrics"""
        extra_fields = {
            'metric_type': 'processing_time',
            'agent_name': agent_name,
            'operation': operation,
            'processing_time_seconds': processing_time,
            'success': success,
            **kwargs
        }
        
        # Create a log record with extra fields
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, __file__, 0,
            f"Processing time: {operation} took {processing_time:.3f}s",
            (), None
        )
        record.extra_fields = extra_fields
        
        self.logger.handle(record)
    
    def log_queue_metrics(self, agent_name: str, queue_size: int, 
                         dlq_size: int = 0, **kwargs):
        """Log message queue metrics"""
        extra_fields = {
            'metric_type': 'queue_metrics',
            'agent_name': agent_name,
            'queue_size': queue_size,
            'dlq_size': dlq_size,
            **kwargs
        }
        
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, __file__, 0,
            f"Queue metrics: {agent_name} queue_size={queue_size} dlq_size={dlq_size}",
            (), None
        )
        record.extra_fields = extra_fields
        
        self.logger.handle(record)
    
    def log_disaster_event(self, event_id: str, disaster_type: str, 
                          confidence: float, verification_score: int = None, 
                          funding_amount: float = None, **kwargs):
        """Log disaster event metrics"""
        extra_fields = {
            'metric_type': 'disaster_event',
            'event_id': event_id,
            'disaster_type': disaster_type,
            'confidence': confidence,
            **kwargs
        }
        
        if verification_score is not None:
            extra_fields['verification_score'] = verification_score
        
        if funding_amount is not None:
            extra_fields['funding_amount'] = funding_amount
        
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, __file__, 0,
            f"Disaster event: {disaster_type} confidence={confidence}",
            (), None
        )
        record.extra_fields = extra_fields
        
        self.logger.handle(record)
    
    def log_blockchain_transaction(self, transaction_id: str, amount: float, 
                                 status: str, tx_hash: str = None, **kwargs):
        """Log blockchain transaction metrics"""
        extra_fields = {
            'metric_type': 'blockchain_transaction',
            'transaction_id': transaction_id,
            'amount': amount,
            'status': status,
            **kwargs
        }
        
        if tx_hash:
            extra_fields['tx_hash'] = tx_hash
        
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, __file__, 0,
            f"Blockchain transaction: {transaction_id} amount={amount} status={status}",
            (), None
        )
        record.extra_fields = extra_fields
        
        self.logger.handle(record)


class SystemMonitor:
    """System monitoring and alerting"""
    
    def __init__(self):
        self.logger = logging.getLogger("system_monitor")
        self.performance_logger = PerformanceLogger("system_performance")
        self.alert_thresholds = {
            'queue_size_warning': 50,
            'queue_size_critical': 100,
            'processing_time_warning': 30.0,  # seconds
            'processing_time_critical': 60.0,
            'error_rate_warning': 0.1,  # 10%
            'error_rate_critical': 0.25  # 25%
        }
    
    def check_queue_health(self, agent_name: str, queue_size: int, dlq_size: int):
        """Check queue health and generate alerts"""
        if queue_size >= self.alert_thresholds['queue_size_critical']:
            self.logger.critical(f"CRITICAL: {agent_name} queue size {queue_size} exceeds critical threshold")
        elif queue_size >= self.alert_thresholds['queue_size_warning']:
            self.logger.warning(f"WARNING: {agent_name} queue size {queue_size} exceeds warning threshold")
        
        if dlq_size > 0:
            self.logger.warning(f"WARNING: {agent_name} has {dlq_size} messages in dead letter queue")
        
        # Log metrics
        self.performance_logger.log_queue_metrics(agent_name, queue_size, dlq_size)
    
    def check_processing_time(self, agent_name: str, operation: str, processing_time: float):
        """Check processing time and generate alerts"""
        if processing_time >= self.alert_thresholds['processing_time_critical']:
            self.logger.critical(f"CRITICAL: {agent_name} {operation} took {processing_time:.3f}s")
        elif processing_time >= self.alert_thresholds['processing_time_warning']:
            self.logger.warning(f"WARNING: {agent_name} {operation} took {processing_time:.3f}s")
        
        # Log metrics
        self.performance_logger.log_processing_time(agent_name, operation, processing_time)
    
    def check_error_rate(self, agent_name: str, error_count: int, total_count: int):
        """Check error rate and generate alerts"""
        if total_count == 0:
            return
        
        error_rate = error_count / total_count
        
        if error_rate >= self.alert_thresholds['error_rate_critical']:
            self.logger.critical(f"CRITICAL: {agent_name} error rate {error_rate:.2%}")
        elif error_rate >= self.alert_thresholds['error_rate_warning']:
            self.logger.warning(f"WARNING: {agent_name} error rate {error_rate:.2%}")
    
    def log_system_stats(self, stats: Dict[str, Any]):
        """Log comprehensive system statistics"""
        self.logger.info("System statistics", extra={'extra_fields': {
            'metric_type': 'system_stats',
            **stats
        }})


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


def log_with_context(logger: logging.Logger, level: int, message: str, **context):
    """Log message with additional context"""
    record = logger.makeRecord(
        logger.name, level, __file__, 0, message, (), None
    )
    record.extra_fields = context
    logger.handle(record)