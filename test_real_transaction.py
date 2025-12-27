#!/usr/bin/env python3
"""
Test real blockchain transaction
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from disaster_management_system.agents.watchtower import WatchtowerAgent
from disaster_management_system.agents.auditor import AuditorAgent
from disaster_management_system.agents.treasurer import TreasurerAgent
from disaster_management_system.shared.logging_config import setup_logging

async def test_real_transaction():
    """Test real blockchain transaction"""
    print("💰 Testing REAL Blockchain Transaction...")
    print("=" * 60)
    
    setup_logging()
    
    # Create agents with real blockchain config
    watchtower_config = {
        'heartbeat_interval': 30,
        'disaster_thresholds': {
            'fire': 0.3,
            'flood': 0.3,
            'structural': 0.4,
            'casualty': 0.5
        }
    }
    
    auditor_config = {
        'heartbeat_interval': 30,
        'verification_threshold': 60
    }
    
    # Treasurer with real blockchain credentials
    treasurer_config = {
        'heartbeat_interval': 30,
        'min_funding_amount': 0.001,  # Small amount for testing
        'max_funding_amount': 0.01,   # Small amount for testing
        'blockchain': {
            'network_url': 'https://sepolia.infura.io/v3/1df86dfd23a442cc8609f6dbe66d5832',
            'private_key': '0x847888bebc95f4ec43485b92093ae632e211c0d2a59d2ebf19a874c00a22144c',
            'gas_limit': 21000,
            'gas_price': 20000000000,
            'default_recipients': {
                'emergency_ngo': '0x5D3f355f0EA186896802878E7Aa0b184469c3033',
                'local_government': '0x5D3f355f0EA186896802878E7Aa0b184469c3033',
                'disaster_relief': '0x5D3f355f0EA186896802878E7Aa0b184469c3033'
            }
        }
    }
    
    # Create agents
    watchtower = WatchtowerAgent(watchtower_config)
    watchtower.disaster_thresholds = watchtower_config['disaster_thresholds']
    
    auditor = AuditorAgent(auditor_config)
    auditor.verification_threshold = 60
    
    treasurer = TreasurerAgent(treasurer_config)
    
    print("🔥 STEP 1: DISASTER DETECTION")
    print("-" * 50)
    
    # Detect disaster
    result = await watchtower.process_test_image('test_images/intense_fire.jpg', (34.0522, -118.2437))
    
    if result:
        print(f"✅ DISASTER DETECTED: {result.disaster_type.upper()}")
        print(f"   Confidence: {result.confidence:.0%}")
        print(f"   Severity: {result.severity_score:.2f}")
        
        print(f"\n🔍 STEP 2: DISASTER VERIFICATION")
        print("-" * 50)
        
        # Verify disaster
        verified_result = await auditor.verify_disaster(result)
        
        if verified_result and verified_result.verification_score >= auditor.verification_threshold:
            print(f"✅ VERIFICATION PASSED: {verified_result.verification_score}/100")
            print(f"   Human Impact: {verified_result.human_impact_estimate} people")
            print(f"   Funding: {verified_result.funding_recommendation:.3f} ETH")
            
            print(f"\n💰 STEP 3: REAL BLOCKCHAIN TRANSACTION")
            print("-" * 50)
            
            # Check if treasurer can connect to blockchain
            connected = await treasurer.blockchain.connect()
            
            if connected:
                print(f"✅ Connected to Sepolia testnet")
                print(f"   Account: {treasurer.blockchain.address}")
                
                # Get current balance
                balance = await treasurer.blockchain.get_balance()
                print(f"   Balance Before: {balance:.4f} ETH")
                
                if balance >= verified_result.funding_recommendation:
                    print(f"\n🚨 EXECUTING REAL TRANSACTION...")
                    
                    # Execute real funding transaction
                    funding_transaction = await treasurer.distribute_funding(verified_result)
                    
                    if funding_transaction:
                        print(f"✅ TRANSACTION INITIATED!")
                        print(f"   Transaction ID: {funding_transaction.transaction_id}")
                        print(f"   Total Amount: {funding_transaction.total_amount:.3f} ETH")
                        print(f"   Recipients: {len(funding_transaction.recipient_addresses)}")
                        print(f"   Status: {funding_transaction.status}")
                        
                        # Wait a bit and check transaction status
                        print(f"\n⏳ Waiting for transaction confirmation...")
                        await asyncio.sleep(10)
                        
                        # Check new balance
                        new_balance = await treasurer.blockchain.get_balance()
                        print(f"   Balance After: {new_balance:.4f} ETH")
                        print(f"   Amount Spent: {balance - new_balance:.4f} ETH")
                        
                        if new_balance < balance:
                            print(f"\n🎉 REAL TRANSACTION SUCCESSFUL!")
                            print(f"   💸 Funds actually transferred from your wallet!")
                            print(f"   🌐 Transaction on Sepolia testnet")
                            print(f"   📋 Transaction hashes: {funding_transaction.transaction_hashes}")
                            return True
                        else:
                            print(f"\n⚠️  Transaction may be pending...")
                            return False
                    else:
                        print(f"❌ Transaction failed to initiate")
                        return False
                else:
                    print(f"❌ Insufficient balance: {balance:.4f} ETH < {verified_result.funding_recommendation:.3f} ETH")
                    return False
            else:
                print(f"❌ Failed to connect to blockchain")
                return False
        else:
            print(f"❌ Verification failed or score too low")
            return False
    else:
        print(f"❌ No disaster detected")
        return False

if __name__ == '__main__':
    success = asyncio.run(test_real_transaction())
    
    if success:
        print(f"\n🏆 REAL BLOCKCHAIN TRANSACTION COMPLETED!")
        print(f"   Your disaster management system made actual transactions!")
    else:
        print(f"\n⚠️  Transaction test incomplete - check logs above")