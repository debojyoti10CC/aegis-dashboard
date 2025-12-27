"""
Auditor Agent - Disaster Verification and Human Impact Assessment
"""

import asyncio
import logging
import random
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from ..shared.base_agent import BaseAgent
from ..shared.models import DisasterEvent, VerifiedEvent


class AuditorAgent(BaseAgent):
    """Agent responsible for verifying disasters and assessing human impact"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("auditor", config)
        self.verification_threshold = 75
        self.historical_data = {}  # Simple in-memory storage for historical patterns
        
        # ML model weights (simplified - in reality these would be trained models)
        self.disaster_weights = {
            'fire': {'confidence_weight': 0.8, 'severity_weight': 0.9, 'location_weight': 0.7},
            'flood': {'confidence_weight': 0.7, 'severity_weight': 0.8, 'location_weight': 0.9},
            'structural': {'confidence_weight': 0.9, 'severity_weight': 0.8, 'location_weight': 0.6},
            'casualty': {'confidence_weight': 0.95, 'severity_weight': 1.0, 'location_weight': 0.8}
        }
        
    async def _processing_loop(self):
        """Main processing loop for disaster verification"""
        self.logger.info("Auditor agent processing loop started")
        
        while self.is_running:
            try:
                # Consume messages from queue
                messages = await self.receive_messages()
                
                for message in messages:
                    await self.process_message(message.payload)
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(5)
    
    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming disaster event for verification"""
        try:
            if 'disaster_event' in message:
                disaster_event = DisasterEvent.from_dict(message['disaster_event'])
                verified_event = await self.verify_disaster(disaster_event)
                
                if verified_event and verified_event.verification_score >= self.verification_threshold:
                    # Send to Treasurer Agent
                    await self.send_message("treasurer", {
                        'verified_event': verified_event.to_dict()
                    })
                    
                    self.logger.info(f"Disaster verified: {disaster_event.disaster_type} "
                                   f"with score {verified_event.verification_score}")
                    
                    return {'status': 'verified', 'verification_score': verified_event.verification_score}
                else:
                    self.logger.info(f"Disaster rejected: {disaster_event.disaster_type} "
                                   f"with score {verified_event.verification_score if verified_event else 0}")
                    return {'status': 'rejected', 'verification_score': verified_event.verification_score if verified_event else 0}
            
            return {'status': 'no_event_to_verify'}
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def verify_disaster(self, disaster_event: DisasterEvent) -> Optional[VerifiedEvent]:
        """Verify disaster event using ML models and cross-validation"""
        try:
            # Multi-model ensemble verification
            verification_scores = []
            
            # Model 1: Confidence-based verification
            confidence_score = await self._verify_by_confidence(disaster_event)
            verification_scores.append(confidence_score)
            
            # Model 2: Historical pattern verification
            historical_score = await self._verify_by_historical_patterns(disaster_event)
            verification_scores.append(historical_score)
            
            # Model 3: Geospatial verification
            geospatial_score = await self._verify_by_geospatial_analysis(disaster_event)
            verification_scores.append(geospatial_score)
            
            # Model 4: Cross-validation with similar events
            cross_validation_score = await self._cross_validate_event(disaster_event)
            verification_scores.append(cross_validation_score)
            
            # Calculate ensemble score
            final_verification_score = int(sum(verification_scores) / len(verification_scores))
            
            # Assess human impact
            human_impact = await self._assess_human_impact(disaster_event)
            
            # Calculate funding recommendation
            funding_recommendation = await self._calculate_funding_recommendation(
                disaster_event, final_verification_score, human_impact
            )
            
            # Store in historical data for future reference
            await self._store_historical_data(disaster_event, final_verification_score)
            
            verified_event = VerifiedEvent(
                event_id=disaster_event.event_id,
                original_event=disaster_event,
                verification_score=final_verification_score,
                human_impact_estimate=human_impact,
                funding_recommendation=funding_recommendation,
                verification_timestamp=datetime.utcnow(),
                audit_details={
                    'confidence_score': confidence_score,
                    'historical_score': historical_score,
                    'geospatial_score': geospatial_score,
                    'cross_validation_score': cross_validation_score,
                    'ensemble_method': 'weighted_average',
                    'verification_models_used': 4,
                    'processing_time': datetime.utcnow().isoformat()
                }
            )
            
            return verified_event
            
        except Exception as e:
            self.logger.error(f"Error verifying disaster: {e}")
            return None
    
    async def _verify_by_confidence(self, disaster_event: DisasterEvent) -> float:
        """Verify disaster based on initial confidence and severity"""
        try:
            disaster_type = disaster_event.disaster_type
            weights = self.disaster_weights.get(disaster_type, self.disaster_weights['fire'])
            
            # Weight the original confidence
            confidence_component = disaster_event.confidence * weights['confidence_weight']
            severity_component = disaster_event.severity_score * weights['severity_weight']
            
            # Combine components
            score = (confidence_component * 0.7) + (severity_component * 0.3)
            
            # Convert to 0-100 scale
            return min(100, score * 100)
            
        except Exception as e:
            self.logger.error(f"Error in confidence verification: {e}")
            return 0.0
    
    async def _verify_by_historical_patterns(self, disaster_event: DisasterEvent) -> float:
        """Verify disaster against historical patterns"""
        try:
            disaster_type = disaster_event.disaster_type
            coordinates = disaster_event.coordinates
            
            # Check if this area has had similar disasters before
            location_key = f"{coordinates[0]:.2f},{coordinates[1]:.2f}"
            
            if location_key in self.historical_data:
                historical_events = self.historical_data[location_key]
                
                # Look for similar disaster types in the area
                similar_events = [e for e in historical_events if e['disaster_type'] == disaster_type]
                
                if similar_events:
                    # Calculate average confidence of similar events
                    avg_confidence = sum(e['confidence'] for e in similar_events) / len(similar_events)
                    
                    # If current event is consistent with historical pattern, boost score
                    consistency_score = 1.0 - abs(disaster_event.confidence - avg_confidence)
                    return min(100, consistency_score * 100)
                else:
                    # New type of disaster in this area - moderate score
                    return 60.0
            else:
                # No historical data for this area - neutral score
                return 70.0
                
        except Exception as e:
            self.logger.error(f"Error in historical verification: {e}")
            return 50.0
    
    async def _verify_by_geospatial_analysis(self, disaster_event: DisasterEvent) -> float:
        """Verify disaster based on geospatial factors"""
        try:
            disaster_type = disaster_event.disaster_type
            coordinates = disaster_event.coordinates
            
            # Simulate geospatial risk factors
            # In reality, this would use real geospatial data
            
            risk_factors = {
                'fire': self._get_fire_risk_factors(coordinates),
                'flood': self._get_flood_risk_factors(coordinates),
                'structural': self._get_structural_risk_factors(coordinates),
                'casualty': self._get_casualty_risk_factors(coordinates)
            }
            
            risk_score = risk_factors.get(disaster_type, 0.5)
            
            # Convert to 0-100 scale
            return min(100, risk_score * 100)
            
        except Exception as e:
            self.logger.error(f"Error in geospatial verification: {e}")
            return 50.0
    
    def _get_fire_risk_factors(self, coordinates: Tuple[float, float]) -> float:
        """Calculate fire risk based on location"""
        # Simulate fire risk based on coordinates
        # Higher risk in certain latitude ranges (dry areas)
        lat, lon = coordinates
        
        # Simulate dry/fire-prone areas
        if 30 <= abs(lat) <= 45:  # Mediterranean, California-like climates
            return 0.8
        elif abs(lat) < 30:  # Tropical areas
            return 0.6
        else:  # Other areas
            return 0.4
    
    def _get_flood_risk_factors(self, coordinates: Tuple[float, float]) -> float:
        """Calculate flood risk based on location"""
        # Simulate flood risk
        lat, lon = coordinates
        
        # Simulate coastal and river areas (higher flood risk)
        if abs(lat) < 10:  # Equatorial regions
            return 0.9
        elif abs(lat) < 30:  # Tropical regions
            return 0.7
        else:
            return 0.5
    
    def _get_structural_risk_factors(self, coordinates: Tuple[float, float]) -> float:
        """Calculate structural damage risk based on location"""
        # Simulate earthquake/structural risk zones
        lat, lon = coordinates
        
        # Simulate seismic activity zones
        if abs(lat) > 35 or abs(lon) > 120:  # Simulate fault lines
            return 0.8
        else:
            return 0.6
    
    def _get_casualty_risk_factors(self, coordinates: Tuple[float, float]) -> float:
        """Calculate casualty risk based on population density simulation"""
        # Simulate population density
        lat, lon = coordinates
        
        # Simulate urban areas (higher casualty risk)
        if abs(lat) < 40 and abs(lon) < 100:  # Simulate populated areas
            return 0.9
        else:
            return 0.5
    
    async def _cross_validate_event(self, disaster_event: DisasterEvent) -> float:
        """Cross-validate event with similar recent events"""
        try:
            # Look for similar events in recent history
            current_time = datetime.utcnow()
            similar_events = []
            
            for location_key, events in self.historical_data.items():
                for event in events:
                    event_time = datetime.fromisoformat(event['timestamp'])
                    time_diff = current_time - event_time
                    
                    # Look for events in the last 30 days
                    if time_diff <= timedelta(days=30):
                        if event['disaster_type'] == disaster_event.disaster_type:
                            similar_events.append(event)
            
            if similar_events:
                # Calculate consistency with recent similar events
                avg_confidence = sum(e['confidence'] for e in similar_events) / len(similar_events)
                consistency = 1.0 - abs(disaster_event.confidence - avg_confidence)
                return min(100, consistency * 100)
            else:
                # No recent similar events - neutral score
                return 70.0
                
        except Exception as e:
            self.logger.error(f"Error in cross-validation: {e}")
            return 50.0
    
    async def _assess_human_impact(self, disaster_event: DisasterEvent) -> int:
        """Assess potential human impact of the disaster"""
        try:
            base_impact = 0
            
            # Base impact by disaster type
            impact_multipliers = {
                'fire': 100,
                'flood': 150,
                'structural': 200,
                'casualty': 500
            }
            
            base_impact = impact_multipliers.get(disaster_event.disaster_type, 100)
            
            # Adjust by severity
            severity_adjusted = base_impact * disaster_event.severity_score
            
            # Adjust by confidence (higher confidence = more reliable impact estimate)
            confidence_adjusted = severity_adjusted * disaster_event.confidence
            
            # Simulate population density factor
            coordinates = disaster_event.coordinates
            population_factor = self._estimate_population_density(coordinates)
            
            final_impact = int(confidence_adjusted * population_factor)
            
            return max(1, min(10000, final_impact))  # Cap between 1 and 10,000
            
        except Exception as e:
            self.logger.error(f"Error assessing human impact: {e}")
            return 100  # Default impact estimate
    
    def _estimate_population_density(self, coordinates: Tuple[float, float]) -> float:
        """Estimate population density based on coordinates"""
        # Simulate population density
        lat, lon = coordinates
        
        # Simulate urban vs rural areas
        if abs(lat) < 40 and abs(lon) < 100:  # Simulate populated regions
            return random.uniform(1.5, 3.0)  # Urban areas
        else:
            return random.uniform(0.5, 1.5)  # Rural areas
    
    async def _calculate_funding_recommendation(self, disaster_event: DisasterEvent, 
                                              verification_score: int, human_impact: int) -> float:
        """Calculate recommended funding amount"""
        try:
            # Base funding by disaster type (in ETH)
            base_funding = {
                'fire': 0.1,
                'flood': 0.15,
                'structural': 0.2,
                'casualty': 0.5
            }
            
            base_amount = base_funding.get(disaster_event.disaster_type, 0.1)
            
            # Adjust by verification score (higher score = more funding)
            verification_factor = verification_score / 100.0
            
            # Adjust by severity
            severity_factor = disaster_event.severity_score
            
            # Adjust by human impact
            impact_factor = min(2.0, human_impact / 1000.0)  # Cap at 2x multiplier
            
            recommended_funding = base_amount * verification_factor * severity_factor * impact_factor
            
            # Cap funding between 0.01 and 2.0 ETH
            return max(0.01, min(2.0, recommended_funding))
            
        except Exception as e:
            self.logger.error(f"Error calculating funding recommendation: {e}")
            return 0.1  # Default funding amount
    
    async def _store_historical_data(self, disaster_event: DisasterEvent, verification_score: int):
        """Store event data for future historical analysis"""
        try:
            coordinates = disaster_event.coordinates
            location_key = f"{coordinates[0]:.2f},{coordinates[1]:.2f}"
            
            event_data = {
                'disaster_type': disaster_event.disaster_type,
                'confidence': disaster_event.confidence,
                'severity': disaster_event.severity_score,
                'verification_score': verification_score,
                'timestamp': disaster_event.timestamp.isoformat()
            }
            
            if location_key not in self.historical_data:
                self.historical_data[location_key] = []
            
            self.historical_data[location_key].append(event_data)
            
            # Keep only last 100 events per location to prevent memory issues
            if len(self.historical_data[location_key]) > 100:
                self.historical_data[location_key] = self.historical_data[location_key][-100:]
                
        except Exception as e:
            self.logger.error(f"Error storing historical data: {e}")
    
    async def get_verification_stats(self) -> Dict[str, Any]:
        """Get verification statistics"""
        try:
            total_locations = len(self.historical_data)
            total_events = sum(len(events) for events in self.historical_data.values())
            
            disaster_type_counts = {}
            for events in self.historical_data.values():
                for event in events:
                    disaster_type = event['disaster_type']
                    disaster_type_counts[disaster_type] = disaster_type_counts.get(disaster_type, 0) + 1
            
            return {
                'total_locations_monitored': total_locations,
                'total_events_processed': total_events,
                'disaster_type_distribution': disaster_type_counts,
                'verification_threshold': self.verification_threshold,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting verification stats: {e}")
            return {}