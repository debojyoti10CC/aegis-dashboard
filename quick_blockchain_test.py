#!/usr/bin/env python3
"""
Quick blockchain test with direct credentials
"""

from web3 import Web3
from eth_account import Account

def test_direct():
    """Test blockchain connection directly"""
    print("🔗 Testing Blockchain Connection...")
    
    # Your credentials from .env
    network_url = "https://sepolia.infura.io/v3/1df86dfd23a442cc8609f6dbe66d5832"
    private_key = "0x847888bebc95f4ec43485b92093ae632e211c0d2a59d2ebf19a874c00a22144c"
    
    print(f"📡 Network URL: {network_url}")
    print(f"🔑 Private Key: ***{private_key[-4:]}")
    
    try:
        # Test Web3 connection
        w3 = Web3(Web3.HTTPProvider(network_url))
        
        if w3.is_connected():
            print("✅ Connected to Sepolia testnet")
            
            # Test account
            account = Account.from_key(private_key)
            address = account.address
            print(f"✅ Account Address: {address}")
            
            # Check balance
            balance_wei = w3.eth.get_balance(address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            print(f"💰 Account Balance: {balance_eth} ETH")
            
            if balance_eth > 0:
                print("✅ Ready for real transactions!")
                return True, address, balance_eth
            else:
                print("⚠️  No ETH balance - get testnet ETH from https://sepoliafaucet.com/")
                print(f"   Send testnet ETH to: {address}")
                return True, address, 0
                
        else:
            print("❌ Failed to connect to Sepolia testnet")
            return False, None, 0
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None, 0

if __name__ == '__main__':
    success, address, balance = test_direct()
    
    if success and balance > 0:
        print(f"\n🎉 BLOCKCHAIN READY FOR REAL TRANSACTIONS!")
        print(f"   Address: {address}")
        print(f"   Balance: {balance} ETH")
        print(f"   Network: Sepolia Testnet")
    elif success and balance == 0:
        print(f"\n⚠️  BLOCKCHAIN CONNECTED BUT NEEDS FUNDS")
        print(f"   Get testnet ETH from: https://sepoliafaucet.com/")
        print(f"   Send to address: {address}")
    else:
        print(f"\n❌ BLOCKCHAIN CONNECTION FAILED")
        print(f"   Check your Infura project ID and private key")