#!/usr/bin/env python3
"""
Test extreme disaster detection
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from disaster_management_system.agents.watchtower import WatchtowerAgent
from disaster_management_system.agents.auditor import AuditorAgent
from disaster_management_system.shared.logging_config import setup_logging

async def test_extreme_disaster():
    """Test extreme disaster detection and verification"""
    print("🔥 Testing Extreme Disaster Detection and Full Pipeline...")
    
    # Setup logging
    setup_logging()
    
    # Create agents
    config = {'heartbeat_interval': 30}
    watchtower = WatchtowerAgent(config)
    auditor = AuditorAgent(config)
    
    # Test extreme fire
    print("\n🔥 Step 1: Watchtower Detection")
    fire_result = await watchtower.process_test_image('test_images/extreme_fire.jpg', (34.0522, -118.2437))
    
    if fire_result:
        print(f"✅ Disaster detected by Watchtower!")
        print(f"   Type: {fire_result.disaster_type}")
        print(f"   Confidence: {fire_result.confidence:.2f}")
        print(f"   Severity: {fire_result.severity_score:.2f}")
        print(f"   Location: {fire_result.coordinates}")
        
        # Test verification
        print(f"\n🔍 Step 2: Auditor Verification")
        verified_result = await auditor.verify_disaster(fire_result)
        
        if verified_result:
            print(f"✅ Disaster verified by Auditor!")
            print(f"   Verification Score: {verified_result.verification_score}/100")
            print(f"   Human Impact: {verified_result.human_impact_estimate} people")
            print(f"   Funding Recommendation: {verified_result.funding_recommendation:.3f} ETH")
            
            if verified_result.verification_score >= 75:
                print(f"\n✅ VERIFICATION PASSED! Score: {verified_result.verification_score}/100")
                print(f"🚨 DISASTER RESPONSE TRIGGERED!")
                
                print(f"\n💰 Step 3: Treasurer Funding Distribution (Simulated)")
                print(f"   Total Funding: {verified_result.funding_recommendation:.3f} ETH")
                print(f"   📍 Emergency NGO (40%): {verified_result.funding_recommendation * 0.4:.3f} ETH")
                print(f"   🏛️  Local Government (30%): {verified_result.funding_recommendation * 0.3:.3f} ETH")
                print(f"   🆘 Disaster Relief (30%): {verified_result.funding_recommendation * 0.3:.3f} ETH")
                
                print(f"\n🎯 COMPLETE PIPELINE SUCCESS!")
                print(f"   ✅ Detection: {fire_result.disaster_type} at {fire_result.confidence:.0%} confidence")
                print(f"   ✅ Verification: {verified_result.verification_score}/100 score")
                print(f"   ✅ Funding: {verified_result.funding_recommendation:.3f} ETH distributed")
                
                if verified_result.funding_recommendation > 0.1:
                    print(f"   🚨 HIGH-VALUE DISASTER: Significant funding triggered!")
                
            else:
                print(f"❌ Verification failed: {verified_result.verification_score}/100 (need ≥75)")
        else:
            print("❌ Auditor verification failed")
    else:
        print("❌ No disaster detected by Watchtower")

if __name__ == '__main__':
    asyncio.run(test_extreme_disaster())