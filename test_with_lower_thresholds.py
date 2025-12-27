#!/usr/bin/env python3
"""
Test with lower detection thresholds
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from disaster_management_system.agents.watchtower import WatchtowerAgent
from disaster_management_system.agents.auditor import AuditorAgent
from disaster_management_system.shared.logging_config import setup_logging

async def test_with_lower_thresholds():
    """Test with more sensitive thresholds"""
    print("🔍 Testing with Lower Detection Thresholds...")
    
    setup_logging()
    
    # Create watchtower with lower thresholds
    config = {
        'heartbeat_interval': 30,
        'disaster_thresholds': {
            'fire': 0.3,      # Lower from 0.6
            'flood': 0.3,     # Lower from 0.5
            'structural': 0.4, # Lower from 0.7
            'casualty': 0.5    # Lower from 0.8
        }
    }
    
    watchtower = WatchtowerAgent(config)
    # Override thresholds
    watchtower.disaster_thresholds = config['disaster_thresholds']
    
    auditor = AuditorAgent({'heartbeat_interval': 30})
    
    # Test all images
    test_images = [
        ('test_images/extreme_fire.jpg', (34.0522, -118.2437), 'Extreme Fire'),
        ('test_images/intense_fire.jpg', (34.0522, -118.2437), 'Intense Fire'),
        ('test_images/fire_disaster.jpg', (34.0522, -118.2437), 'Fire Disaster'),
        ('test_images/flood_disaster.jpg', (29.7604, -95.3698), 'Flood Disaster'),
        ('test_images/structural_damage.jpg', (37.7749, -122.4194), 'Structural Damage')
    ]
    
    best_result = None
    best_score = 0
    
    for image_path, coords, name in test_images:
        if not os.path.exists(image_path):
            continue
            
        print(f"\n🔍 Testing {name}:")
        result = await watchtower.process_test_image(image_path, coords)
        
        if result:
            print(f"✅ {result.disaster_type.title()} detected!")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Severity: {result.severity_score:.2f}")
            
            if result.confidence > best_score:
                best_result = result
                best_score = result.confidence
        else:
            print(f"❌ No disaster detected")
    
    # Test verification on best result
    if best_result:
        print(f"\n🏆 Best Detection: {best_result.disaster_type} with {best_result.confidence:.2f} confidence")
        print(f"\n🔍 Testing Auditor Verification:")
        
        verified_result = await auditor.verify_disaster(best_result)
        
        if verified_result:
            print(f"✅ Verification complete!")
            print(f"   Verification Score: {verified_result.verification_score}/100")
            print(f"   Human Impact: {verified_result.human_impact_estimate} people")
            print(f"   Funding: {verified_result.funding_recommendation:.3f} ETH")
            
            if verified_result.verification_score >= 75:
                print(f"\n🎉 FULL PIPELINE SUCCESS!")
                print(f"   Detection → Verification → Funding Distribution")
                print(f"   {best_result.disaster_type.title()} disaster would receive {verified_result.funding_recommendation:.3f} ETH")
            else:
                print(f"\n⚠️  Verification score too low: {verified_result.verification_score}/100")
                print(f"   (Need ≥75 for funding approval)")
        else:
            print("❌ Verification failed")
    else:
        print("\n❌ No disasters detected with current thresholds")
        print("💡 Try creating images with more obvious disaster indicators")

if __name__ == '__main__':
    asyncio.run(test_with_lower_thresholds())