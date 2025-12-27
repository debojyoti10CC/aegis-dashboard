"""
Core data models for the disaster management system
"""

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class ImageInput:
    """Input data structure for satellite/drone imagery"""
    image_data: bytes
    timestamp: datetime
    coordinates: Optional[Tuple[float, float]]
    source_type: str  # "satellite" | "drone"
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'image_data': self.image_data.hex() if self.image_data else None,
            'timestamp': self.timestamp.isoformat(),
            'coordinates': self.coordinates,
            'source_type': self.source_type,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageInput':
        """Create from dictionary"""
        return cls(
            image_data=bytes.fromhex(data['image_data']) if data['image_data'] else b'',
            timestamp=datetime.fromisoformat(data['timestamp']),
            coordinates=tuple(data['coordinates']) if data['coordinates'] else None,
            source_type=data['source_type'],
            metadata=data['metadata']
        )


@dataclass
class DisasterEvent:
    """Disaster event detected by Watchtower Agent"""
    event_id: str
    disaster_type: str  # "fire" | "flood" | "structural" | "casualty"
    severity_score: float  # 0.0 to 1.0
    coordinates: Tuple[float, float]
    confidence: float
    timestamp: datetime
    image_analysis: Dict[str, Any]
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'disaster_type': self.disaster_type,
            'severity_score': self.severity_score,
            'coordinates': list(self.coordinates),
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'image_analysis': self.image_analysis
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DisasterEvent':
        """Create from dictionary"""
        return cls(
            event_id=data['event_id'],
            disaster_type=data['disaster_type'],
            severity_score=data['severity_score'],
            coordinates=tuple(data['coordinates']),
            confidence=data['confidence'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            image_analysis=data['image_analysis']
        )


@dataclass
class VerifiedEvent:
    """Verified disaster event from Auditor Agent"""
    event_id: str
    original_event: DisasterEvent
    verification_score: int  # 0-100
    human_impact_estimate: int
    funding_recommendation: float
    verification_timestamp: datetime
    audit_details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'original_event': self.original_event.to_dict(),
            'verification_score': self.verification_score,
            'human_impact_estimate': self.human_impact_estimate,
            'funding_recommendation': self.funding_recommendation,
            'verification_timestamp': self.verification_timestamp.isoformat(),
            'audit_details': self.audit_details
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerifiedEvent':
        """Create from dictionary"""
        return cls(
            event_id=data['event_id'],
            original_event=DisasterEvent.from_dict(data['original_event']),
            verification_score=data['verification_score'],
            human_impact_estimate=data['human_impact_estimate'],
            funding_recommendation=data['funding_recommendation'],
            verification_timestamp=datetime.fromisoformat(data['verification_timestamp']),
            audit_details=data['audit_details']
        )


@dataclass
class FundingTransaction:
    """Blockchain funding transaction from Treasurer Agent"""
    transaction_id: str
    event_id: str
    recipient_addresses: List[str]
    amounts: List[float]
    transaction_hashes: List[str]
    total_amount: float
    status: str  # "pending" | "confirmed" | "failed"
    timestamp: datetime
    
    def __post_init__(self):
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'transaction_id': self.transaction_id,
            'event_id': self.event_id,
            'recipient_addresses': self.recipient_addresses,
            'amounts': self.amounts,
            'transaction_hashes': self.transaction_hashes,
            'total_amount': self.total_amount,
            'status': self.status,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FundingTransaction':
        """Create from dictionary"""
        return cls(
            transaction_id=data['transaction_id'],
            event_id=data['event_id'],
            recipient_addresses=data['recipient_addresses'],
            amounts=data['amounts'],
            transaction_hashes=data['transaction_hashes'],
            total_amount=data['total_amount'],
            status=data['status'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


@dataclass
class AgentStatus:
    """Agent status information"""
    agent_name: str
    status: str  # "running" | "stopped" | "error"
    last_heartbeat: datetime
    processed_count: int
    error_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentStatus':
        return cls(
            agent_name=data['agent_name'],
            status=data['status'],
            last_heartbeat=datetime.fromisoformat(data['last_heartbeat']),
            processed_count=data['processed_count'],
            error_count=data['error_count']
        )


@dataclass
class QueueMessage:
    """Message queue data structure"""
    message_id: str
    sender: str
    recipient: str
    payload: Dict[str, Any]
    timestamp: datetime
    retry_count: int = 0
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        data = {
            'message_id': self.message_id,
            'sender': self.sender,
            'recipient': self.recipient,
            'payload': self.payload,
            'timestamp': self.timestamp.isoformat(),
            'retry_count': self.retry_count
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'QueueMessage':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls(
            message_id=data['message_id'],
            sender=data['sender'],
            recipient=data['recipient'],
            payload=data['payload'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            retry_count=data['retry_count']
        )