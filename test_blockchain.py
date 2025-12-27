#!/usr/bin/env python3
"""
Test blockchain connection with your credentials
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from disaster_management_system.shared.blockchain import BlockchainManager

def test_blockchain():
    """Test blockchain connection"""
    print("🔗 Testing Blockchain Connection...")
    
    # Get credentials from environment
    network_url = os.getenv('BLOCKCHAIN_NETWORK_URL')
    private_key = os.getenv('BLOCKCHAIN_PRIVATE_KEY')
    
    print(f"📡 Network URL: {network_url}")
    print(f"🔑 Private Key: {'***' + private_key[-4:] if private_key and len(private_key) > 4 else 'Not set'}")
    
    # Test blockchain manager
    config = {
        'network_url': network_url,
        'private_key': private_key
    }
    
    blockchain = BlockchainManager(config)
    
    if blockchain.account:
        print(f"✅ Account Address: {blockchain.address}")
        
        # Test connection
        try:
            if blockchain.w3.is_connected():
                print("✅ Connected to Sepolia testnet")
                
                # Check balance
                balance_wei = blockchain.w3.eth.get_balance(blockchain.address)
                balance_eth = blockchain.w3.from_wei(balance_wei, 'ether')
                print(f"💰 Account Balance: {balance_eth} ETH")
                
                if balance_eth > 0:
                    print("✅ Ready for transactions!")
                    return True
                else:
                    print("⚠️  No ETH balance - get testnet ETH from https://sepoliafaucet.com/")
                    return True  # Connection works, just needs funds
                
            else:
                print("❌ Failed to connect to blockchain network")
                return False
                
        except Exception as e:
            print(f"❌ Blockchain connection error: {e}")
            return False
    else:
        print("❌ No valid blockchain account configured")
        return False

if __name__ == '__main__':
    success = test_blockchain()
    if success:
        print("\n🎉 Blockchain is ready! You can now run the full system:")
        print("python run.py start")
    else:
        print("\n⚠️  Please check your blockchain credentials in .env file")
        print("1. Update BLOCKCHAIN_NETWORK_URL with your Infura project ID")
        print("2. Update BLOCKCHAIN_PRIVATE_KEY with your Sepolia private key")
        print("3. Make sure you have testnet ETH from https://sepoliafaucet.com/")