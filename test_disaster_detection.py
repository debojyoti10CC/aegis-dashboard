#!/usr/bin/env python3
"""
Test disaster detection directly
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from disaster_management_system.agents.watchtower import WatchtowerAgent
from disaster_management_system.shared.models import ImageInput
from disaster_management_system.shared.logging_config import setup_logging

async def test_disaster_detection():
    """Test disaster detection directly"""
    print("🔍 Testing Disaster Detection...")
    
    # Setup logging
    setup_logging()
    
    # Create watchtower agent
    config = {'heartbeat_interval': 30}
    watchtower = WatchtowerAgent(config)
    
    # Test fire image
    print("\n🔥 Testing Fire Detection:")
    fire_result = await watchtower.process_test_image('test_images/intense_fire.jpg', (34.0522, -118.2437))
    
    if fire_result:
        print(f"✅ Fire detected!")
        print(f"   Type: {fire_result.disaster_type}")
        print(f"   Confidence: {fire_result.confidence:.2f}")
        print(f"   Severity: {fire_result.severity_score:.2f}")
        print(f"   Location: {fire_result.coordinates}")
    else:
        print("❌ No fire detected")
    
    # Test structural damage
    print("\n🏢 Testing Structural Damage Detection:")
    damage_result = await watchtower.process_test_image('test_images/structural_damage.jpg', (37.7749, -122.4194))
    
    if damage_result:
        print(f"✅ Structural damage detected!")
        print(f"   Type: {damage_result.disaster_type}")
        print(f"   Confidence: {damage_result.confidence:.2f}")
        print(f"   Severity: {damage_result.severity_score:.2f}")
        print(f"   Location: {damage_result.coordinates}")
    else:
        print("❌ No structural damage detected")
    
    # Test flood image
    print("\n🌊 Testing Flood Detection:")
    flood_result = await watchtower.process_test_image('test_images/flood_disaster.jpg', (29.7604, -95.3698))
    
    if flood_result:
        print(f"✅ Flood detected!")
        print(f"   Type: {flood_result.disaster_type}")
        print(f"   Confidence: {flood_result.confidence:.2f}")
        print(f"   Severity: {flood_result.severity_score:.2f}")
        print(f"   Location: {flood_result.coordinates}")
    else:
        print("❌ No flood detected")
    
    # Test auditor verification
    best_result = None
    if fire_result and fire_result.confidence > 0.5:
        best_result = fire_result
    elif damage_result and damage_result.confidence > 0.5:
        best_result = damage_result
    elif flood_result and flood_result.confidence > 0.5:
        best_result = flood_result
    
    if best_result:
        print(f"\n🔍 Testing Auditor Verification for {best_result.disaster_type}:")
        from disaster_management_system.agents.auditor import AuditorAgent
        
        auditor = AuditorAgent(config)
        verified_result = await auditor.verify_disaster(best_result)
        
        if verified_result:
            print(f"✅ Disaster verified!")
            print(f"   Verification Score: {verified_result.verification_score}/100")
            print(f"   Human Impact: {verified_result.human_impact_estimate} people")
            print(f"   Funding Recommendation: {verified_result.funding_recommendation:.3f} ETH")
            
            if verified_result.verification_score >= 75:
                print("✅ Passes verification threshold - would trigger funding!")
                
                # Show what would happen with blockchain
                print(f"\n💰 Blockchain Transaction (Simulated):")
                print(f"   Total Funding: {verified_result.funding_recommendation:.3f} ETH")
                print(f"   Emergency NGO (40%): {verified_result.funding_recommendation * 0.4:.3f} ETH")
                print(f"   Local Government (30%): {verified_result.funding_recommendation * 0.3:.3f} ETH")
                print(f"   Disaster Relief (30%): {verified_result.funding_recommendation * 0.3:.3f} ETH")
            else:
                print("❌ Below verification threshold - funding not triggered")
        else:
            print("❌ Verification failed")
    else:
        print("\n❌ No disasters detected with sufficient confidence for verification")

if __name__ == '__main__':
    asyncio.run(test_disaster_detection())