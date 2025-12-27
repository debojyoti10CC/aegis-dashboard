#!/usr/bin/env python3
"""
Test simple blockchain transaction to your own address
"""

import asyncio
from web3 import Web3
from eth_account import Account

async def test_simple_transaction():
    """Test sending a small amount to your own address"""
    print("💰 Testing Simple Blockchain Transaction...")
    print("=" * 50)
    
    # Your credentials
    network_url = "https://sepolia.infura.io/v3/1df86dfd23a442cc8609f6dbe66d5832"
    private_key = "0x847888bebc95f4ec43485b92093ae632e211c0d2a59d2ebf19a874c00a22144c"
    
    try:
        # Setup Web3
        w3 = Web3(Web3.HTTPProvider(network_url))
        account = Account.from_key(private_key)
        address = account.address
        
        print(f"📍 Your Address: {address}")
        
        # Check initial balance
        balance_wei = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        print(f"💰 Initial Balance: {balance_eth:.4f} ETH")
        
        if balance_eth < 0.001:
            print("❌ Insufficient balance for transaction")
            return False
        
        # Create a small transaction to yourself (this will just cost gas)
        amount_to_send = 0.0001  # Very small amount
        amount_wei = w3.to_wei(amount_to_send, 'ether')
        
        # Get current nonce
        nonce = w3.eth.get_transaction_count(address)
        
        # Estimate gas price
        gas_price = w3.eth.gas_price
        
        # Build transaction
        transaction = {
            'to': address,  # Send to yourself
            'value': amount_wei,
            'gas': 21000,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': 11155111  # Sepolia chain ID
        }
        
        print(f"\n🚀 Sending Transaction...")
        print(f"   To: {address}")
        print(f"   Amount: {amount_to_send} ETH")
        print(f"   Gas Price: {w3.from_wei(gas_price, 'gwei')} Gwei")
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        
        print(f"✅ Transaction Sent!")
        print(f"   Hash: {tx_hash_hex}")
        print(f"   View on Etherscan: https://sepolia.etherscan.io/tx/{tx_hash_hex}")
        
        # Wait for confirmation
        print(f"\n⏳ Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status == 1:
            print(f"✅ Transaction Confirmed!")
            print(f"   Block: {receipt.blockNumber}")
            print(f"   Gas Used: {receipt.gasUsed}")
            
            # Check new balance
            new_balance_wei = w3.eth.get_balance(address)
            new_balance_eth = w3.from_wei(new_balance_wei, 'ether')
            gas_cost = w3.from_wei(receipt.gasUsed * gas_price, 'ether')
            
            print(f"\n💰 Balance Update:")
            print(f"   Before: {balance_eth:.4f} ETH")
            print(f"   After: {new_balance_eth:.4f} ETH")
            print(f"   Gas Cost: {gas_cost:.4f} ETH")
            print(f"   Net Change: {new_balance_eth - balance_eth:.4f} ETH")
            
            print(f"\n🎉 REAL BLOCKCHAIN TRANSACTION SUCCESSFUL!")
            print(f"   Your funds actually moved on Sepolia testnet!")
            return True
        else:
            print(f"❌ Transaction failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = asyncio.run(test_simple_transaction())
    
    if success:
        print(f"\n🏆 BLOCKCHAIN SYSTEM WORKING!")
        print(f"   Ready for disaster management transactions")
    else:
        print(f"\n⚠️  Transaction failed - check error above")