"""
Watchtower Agent - Disaster Detection from Satellite/Drone Imagery
"""

import asyncio
import cv2
import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from PIL import Image
import io

from ..shared.base_agent import BaseAgent
from ..shared.models import DisasterEvent, ImageInput
import uuid


class WatchtowerAgent(BaseAgent):
    """Agent responsible for processing imagery and detecting disasters"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("watchtower", config)
        self.disaster_thresholds = {
            'fire': 0.6,
            'flood': 0.5,
            'structural': 0.7,
            'casualty': 0.8
        }
        
    async def _processing_loop(self):
        """Main processing loop for image analysis"""
        self.logger.info("Watchtower agent processing loop started")
        
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
        """Process incoming image data"""
        try:
            # Parse image input
            if 'image_input' in message:
                image_input = ImageInput.from_dict(message['image_input'])
                disaster_event = await self.analyze_image(image_input)
                
                if disaster_event:
                    # Send to Auditor Agent
                    await self.send_message("auditor", {
                        'disaster_event': disaster_event.to_dict()
                    })
                    
                    self.logger.info(f"Disaster detected: {disaster_event.disaster_type} "
                                   f"at {disaster_event.coordinates} with confidence {disaster_event.confidence}")
                    
                    return {'status': 'processed', 'event_id': disaster_event.event_id}
            
            return {'status': 'no_disaster_detected'}
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def analyze_image(self, image_input: ImageInput) -> Optional[DisasterEvent]:
        """Analyze image for disaster indicators"""
        try:
            # Convert bytes to OpenCV image
            image = self._bytes_to_cv2_image(image_input.image_data)
            if image is None:
                return None
            
            # Extract coordinates from metadata or image_input
            coordinates = image_input.coordinates or self._extract_coordinates(image_input.metadata)
            if not coordinates:
                coordinates = (0.0, 0.0)  # Default coordinates
            
            # Perform disaster detection
            disaster_results = await self._detect_disasters(image)
            
            # Find the highest confidence disaster
            best_disaster = None
            best_confidence = 0.0
            
            for disaster_type, confidence in disaster_results.items():
                if confidence > self.disaster_thresholds[disaster_type] and confidence > best_confidence:
                    best_disaster = disaster_type
                    best_confidence = confidence
            
            if best_disaster:
                # Calculate severity based on disaster type and confidence
                severity_score = self._calculate_severity(best_disaster, best_confidence, image)
                
                disaster_event = DisasterEvent(
                    event_id="",  # Will be auto-generated
                    disaster_type=best_disaster,
                    severity_score=severity_score,
                    coordinates=coordinates,
                    confidence=best_confidence,
                    timestamp=datetime.utcnow(),
                    image_analysis={
                        'all_detections': disaster_results,
                        'image_size': image.shape[:2],
                        'source_type': image_input.source_type,
                        'processing_timestamp': datetime.utcnow().isoformat()
                    }
                )
                
                return disaster_event
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing image: {e}")
            return None

    async def process_sensor_data(self, data: Dict[str, Any]) -> Optional[DisasterEvent]:
        """Process sensor data from hardware (ESP32)"""
        try:
            self.logger.info(f"Processing sensor data: {data}")
            
            # Check if this is a disaster event
            if data.get('type') == 'disaster_event':
                disaster_type = data.get('sensor_type', 'unknown')
                confidence = float(data.get('confidence', 0)) / 100.0
                severity = float(data.get('severity', 0.5))
                
                # Parse location string "lat,lon"
                location_str = data.get('location', '0,0')
                try:
                    lat, lon = map(float, location_str.split(','))
                    coordinates = (lat, lon)
                except:
                    coordinates = (0.0, 0.0)

                # Create disaster event
                disaster_event = DisasterEvent(
                    event_id=str(uuid.uuid4()),
                    disaster_type=disaster_type,
                    severity_score=severity,
                    coordinates=coordinates,
                    confidence=confidence,
                    timestamp=datetime.utcnow(),
                    image_analysis={
                        'source': 'hardware_sensor',
                        'raw_data': data,
                        'processing_timestamp': datetime.utcnow().isoformat()
                    }
                )
                
                # Forward to auditor immediately
                await self.send_message("auditor", {
                    'disaster_event': disaster_event.to_dict()
                })
                
                return disaster_event
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error processing sensor data: {e}")
            return None
    
    def _bytes_to_cv2_image(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """Convert bytes to OpenCV image"""
        try:
            # Convert bytes to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert PIL to OpenCV format
            cv2_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return cv2_image
        except Exception as e:
            self.logger.error(f"Error converting bytes to image: {e}")
            return None
    
    def _extract_coordinates(self, metadata: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """Extract GPS coordinates from image metadata"""
        try:
            # Try different metadata formats
            if 'gps' in metadata:
                gps = metadata['gps']
                if 'latitude' in gps and 'longitude' in gps:
                    return (float(gps['latitude']), float(gps['longitude']))
            
            if 'coordinates' in metadata:
                coords = metadata['coordinates']
                if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                    return (float(coords[0]), float(coords[1]))
            
            # Default coordinates if not found
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting coordinates: {e}")
            return None
    
    async def _detect_disasters(self, image: np.ndarray) -> Dict[str, float]:
        """Detect various types of disasters in the image"""
        results = {}
        
        # Fire detection (looking for red/orange areas and smoke)
        results['fire'] = await self._detect_fire(image)
        
        # Flood detection (looking for water coverage)
        results['flood'] = await self._detect_flood(image)
        
        # Structural damage detection
        results['structural'] = await self._detect_structural_damage(image)
        
        # Casualty detection (simplified - looking for human-like shapes)
        results['casualty'] = await self._detect_casualties(image)
        
        return results
    
    async def _detect_fire(self, image: np.ndarray) -> float:
        """Detect fire indicators in the image"""
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define range for fire colors (red, orange, yellow)
            lower_fire1 = np.array([0, 50, 50])
            upper_fire1 = np.array([10, 255, 255])
            
            lower_fire2 = np.array([170, 50, 50])
            upper_fire2 = np.array([180, 255, 255])
            
            # Create masks for fire colors
            mask1 = cv2.inRange(hsv, lower_fire1, upper_fire1)
            mask2 = cv2.inRange(hsv, lower_fire2, upper_fire2)
            fire_mask = cv2.bitwise_or(mask1, mask2)
            
            # Calculate fire area percentage
            fire_pixels = cv2.countNonZero(fire_mask)
            total_pixels = image.shape[0] * image.shape[1]
            fire_percentage = fire_pixels / total_pixels
            
            # Look for smoke (gray areas)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            smoke_mask = cv2.inRange(gray, 100, 200)
            smoke_pixels = cv2.countNonZero(smoke_mask)
            smoke_percentage = smoke_pixels / total_pixels
            
            # Combine fire and smoke indicators
            confidence = min(1.0, (fire_percentage * 2) + (smoke_percentage * 0.5))
            
            return confidence
            
        except Exception as e:
            self.logger.error(f"Error in fire detection: {e}")
            return 0.0
    
    async def _detect_flood(self, image: np.ndarray) -> float:
        """Detect flood indicators in the image"""
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define range for water colors (blue, dark blue)
            lower_water = np.array([100, 50, 20])
            upper_water = np.array([130, 255, 255])
            
            water_mask = cv2.inRange(hsv, lower_water, upper_water)
            
            # Calculate water coverage
            water_pixels = cv2.countNonZero(water_mask)
            total_pixels = image.shape[0] * image.shape[1]
            water_percentage = water_pixels / total_pixels
            
            # Look for unusual water patterns (flooding vs normal water bodies)
            # This is a simplified approach - in reality, you'd use more sophisticated ML models
            confidence = min(1.0, water_percentage * 1.5)
            
            return confidence
            
        except Exception as e:
            self.logger.error(f"Error in flood detection: {e}")
            return 0.0
    
    async def _detect_structural_damage(self, image: np.ndarray) -> float:
        """Detect structural damage in the image"""
        try:
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Look for irregular patterns that might indicate damage
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analyze contour irregularity
            irregular_score = 0.0
            for contour in contours:
                if cv2.contourArea(contour) > 1000:  # Only consider significant contours
                    # Calculate contour irregularity
                    perimeter = cv2.arcLength(contour, True)
                    area = cv2.contourArea(contour)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        irregular_score += (1 - circularity)
            
            # Normalize the score
            confidence = min(1.0, irregular_score / len(contours) if contours else 0.0)
            
            return confidence
            
        except Exception as e:
            self.logger.error(f"Error in structural damage detection: {e}")
            return 0.0
    
    async def _detect_casualties(self, image: np.ndarray) -> float:
        """Detect potential casualties in the image"""
        try:
            # This is a simplified approach - in reality, you'd use YOLO or similar
            # for human detection
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Use Haar cascades for basic human detection (if available)
            # For now, we'll use a simple approach based on skin color detection
            
            # Convert to HSV for skin color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define range for skin colors
            lower_skin = np.array([0, 20, 70])
            upper_skin = np.array([20, 255, 255])
            
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # Calculate skin area
            skin_pixels = cv2.countNonZero(skin_mask)
            total_pixels = image.shape[0] * image.shape[1]
            skin_percentage = skin_pixels / total_pixels
            
            # This is a very basic approach - real implementation would use
            # trained models for human detection
            confidence = min(1.0, skin_percentage * 3)
            
            return confidence
            
        except Exception as e:
            self.logger.error(f"Error in casualty detection: {e}")
            return 0.0
    
    def _calculate_severity(self, disaster_type: str, confidence: float, image: np.ndarray) -> float:
        """Calculate disaster severity score"""
        try:
            base_severity = confidence
            
            # Adjust based on disaster type
            type_multipliers = {
                'fire': 1.2,
                'flood': 1.0,
                'structural': 1.1,
                'casualty': 1.5
            }
            
            severity = base_severity * type_multipliers.get(disaster_type, 1.0)
            
            # Consider image size (larger affected areas = higher severity)
            height, width = image.shape[:2]
            size_factor = min(1.2, (height * width) / (1920 * 1080))  # Normalize to 1080p
            
            severity *= size_factor
            
            return min(1.0, severity)
            
        except Exception as e:
            self.logger.error(f"Error calculating severity: {e}")
            return confidence
    
    async def process_test_image(self, image_path: str, coordinates: Tuple[float, float] = None):
        """Process a test image file (for testing purposes)"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            image_input = ImageInput(
                image_data=image_data,
                timestamp=datetime.utcnow(),
                coordinates=coordinates,
                source_type="test",
                metadata={}
            )
            
            result = await self.analyze_image(image_input)
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing test image: {e}")
            return None