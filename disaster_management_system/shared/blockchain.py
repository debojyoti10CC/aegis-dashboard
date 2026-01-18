"""
Blockchain integration for Sepolia testnet transactions
"""

import logging
import os
from typing import Dict, Any, List, Optional
from web3 import Web3
from eth_account import Account
from datetime import datetime
import asyncio


class BlockchainManager:
    """Manages blockchain interactions for disaster funding"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("blockchain")
        
        # Sepolia testnet configuration - read from environment variables first
        self.network_url = (
            os.getenv('BLOCKCHAIN_NETWORK_URL') or 
            config.get('network_url', 'https://sepolia.infura.io/v3/YOUR_PROJECT_ID')
        )
        self.private_key = (
            os.getenv('BLOCKCHAIN_PRIVATE_KEY') or 
            config.get('private_key', '')
        )
        self.gas_limit = config.get('gas_limit', 21000)
        self.gas_price = config.get('gas_price', 20000000000)  # 20 Gwei
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.network_url))
        
        # Default recipient addresses (NGOs, government agencies) - using your address for testing
        self.default_recipients = config.get('default_recipients', {
            'emergency_ngo': os.getenv('EMERGENCY_NGO_ADDRESS', '0x5D3f355f0EA186896802878E7Aa0b184469c3033'),
            'local_government': os.getenv('LOCAL_GOVERNMENT_ADDRESS', '0x5D3f355f0EA186896802878E7Aa0b184469c3033'),
            'disaster_relief': os.getenv('DISASTER_RELIEF_ADDRESS', '0x5D3f355f0EA186896802878E7Aa0b184469c3033')
        })
        
        # Account setup
        if self.private_key and self.private_key != 'YOUR_ACTUAL_PRIVATE_KEY_HERE':
            try:
                self.account = Account.from_key(self.private_key)
                self.address = self.account.address
                self.logger.info(f"Blockchain account initialized: {self.address}")
            except Exception as e:
                self.logger.error(f"Invalid private key: {e}")
                self.account = None
                self.address = None
        else:
            self.account = None
            self.address = None
            self.logger.warning("No valid private key provided - blockchain functionality disabled")
            
    async def connect(self) -> bool:
        """Connect to blockchain network"""
        try:
            if not self.w3.is_connected():
                self.logger.error("Failed to connect to blockchain network")
                return False
            
            # Check if account is set up
            if not self.account:
                self.logger.error("No private key configured")
                return False
            
            # Check account balance
            balance = await self.get_balance()
            self.logger.info(f"Connected to Sepolia testnet. Account: {self.address}, Balance: {balance} ETH")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to blockchain: {e}")
            return False
    
    async def get_balance(self, address: str = None) -> float:
        """Get ETH balance for an address"""
        try:
            target_address = address or self.address
            if not target_address:
                return 0.0
            
            balance_wei = self.w3.eth.get_balance(target_address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            
            return float(balance_eth)
            
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            return 0.0
    
    async def send_transaction(self, to_address: str, amount_eth: float, 
                             gas_limit: int = None, gas_price: int = None) -> Optional[str]:
        """Send ETH transaction"""
        try:
            if not self.account:
                self.logger.error("No account configured for transactions")
                return None
            
            # Validate recipient address
            if not self.w3.is_address(to_address):
                self.logger.error(f"Invalid recipient address: {to_address}")
                return None
            
            # Convert to checksum address
            to_address = self.w3.to_checksum_address(to_address)
            
            # Convert ETH to Wei
            amount_wei = self.w3.to_wei(amount_eth, 'ether')
            
            # Get current nonce
            nonce = self.w3.eth.get_transaction_count(self.address)
            
            # Build transaction
            transaction = {
                'to': to_address,
                'value': amount_wei,
                'gas': gas_limit or self.gas_limit,
                'gasPrice': gas_price or self.gas_price,
                'nonce': nonce,
                'chainId': 11155111  # Sepolia chain ID
            }
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            self.logger.info(f"Transaction sent: {tx_hash_hex}")
            return tx_hash_hex
            
        except Exception as e:
            self.logger.error(f"Error sending transaction: {e}")
            return None
    
    async def send_multiple_transactions(self, recipients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Send multiple transactions to different recipients"""
        results = []
        
        for recipient in recipients:
            address = recipient.get('address')
            amount = recipient.get('amount', 0.0)
            recipient_type = recipient.get('type', 'unknown')
            
            if not address or amount <= 0:
                results.append({
                    'address': address,
                    'amount': amount,
                    'type': recipient_type,
                    'status': 'failed',
                    'error': 'Invalid address or amount'
                })
                continue
            
            # Send transaction
            tx_hash = await self.send_transaction(address, amount)
            
            if tx_hash:
                results.append({
                    'address': address,
                    'amount': amount,
                    'type': recipient_type,
                    'status': 'sent',
                    'transaction_hash': tx_hash
                })
            else:
                results.append({
                    'address': address,
                    'amount': amount,
                    'type': recipient_type,
                    'status': 'failed',
                    'error': 'Transaction failed'
                })
            
            # Small delay between transactions to avoid nonce issues
            await asyncio.sleep(1)
        
        return results
    
    async def wait_for_confirmation(self, tx_hash: str, timeout: int = 300) -> Optional[Dict[str, Any]]:
        """Wait for transaction confirmation"""
        try:
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            
            return {
                'transaction_hash': tx_hash,
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'status': 'confirmed' if receipt.status == 1 else 'failed',
                'confirmation_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error waiting for confirmation: {e}")
            return {
                'transaction_hash': tx_hash,
                'status': 'timeout',
                'error': str(e)
            }
    
    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction status"""
        try:
            # Try to get transaction receipt
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            return {
                'transaction_hash': tx_hash,
                'status': 'confirmed' if receipt.status == 1 else 'failed',
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed
            }
            
        except Exception:
            # Transaction might be pending
            try:
                tx = self.w3.eth.get_transaction(tx_hash)
                return {
                    'transaction_hash': tx_hash,
                    'status': 'pending',
                    'gas_price': tx.gasPrice,
                    'value': self.w3.from_wei(tx.value, 'ether')
                }
            except Exception as e:
                return {
                    'transaction_hash': tx_hash,
                    'status': 'not_found',
                    'error': str(e)
                }
    
    def get_default_recipients(self, disaster_type: str) -> List[Dict[str, Any]]:
        """Get default recipient addresses based on disaster type"""
        recipients = []
        
        # Base recipients for all disasters
        recipients.append({
            'address': self.default_recipients['emergency_ngo'],
            'type': 'emergency_ngo',
            'percentage': 0.4
        })
        
        recipients.append({
            'address': self.default_recipients['local_government'],
            'type': 'local_government',
            'percentage': 0.3
        })
        
        recipients.append({
            'address': self.default_recipients['disaster_relief'],
            'type': 'disaster_relief',
            'percentage': 0.3
        })
        
        # Adjust percentages based on disaster type
        if disaster_type == 'casualty':
            # More funding to emergency services for casualties
            recipients[0]['percentage'] = 0.6  # Emergency NGO
            recipients[1]['percentage'] = 0.3  # Government
            recipients[2]['percentage'] = 0.1  # Disaster relief
        elif disaster_type == 'structural':
            # More funding to government for infrastructure
            recipients[0]['percentage'] = 0.2  # Emergency NGO
            recipients[1]['percentage'] = 0.6  # Government
            recipients[2]['percentage'] = 0.2  # Disaster relief
        
        return recipients
    
    def calculate_recipient_amounts(self, total_amount: float, recipients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate individual amounts for each recipient"""
        result = []
        
        for recipient in recipients:
            amount = total_amount * recipient['percentage']
            result.append({
                'address': recipient['address'],
                'amount': amount,
                'type': recipient['type'],
                'percentage': recipient['percentage']
            })
        
        return result
    
    async def estimate_gas_price(self) -> int:
        """Estimate current gas price"""
        try:
            gas_price = self.w3.eth.gas_price
            # Add 10% buffer
            return int(gas_price * 1.1)
        except Exception as e:
            self.logger.error(f"Error estimating gas price: {e}")
            return self.gas_price
    
    async def validate_address(self, address: str) -> bool:
        """Validate Ethereum address"""
        try:
            return self.w3.is_address(address) and self.w3.is_checksum_address(address)
        except Exception:
            return False
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            latest_block = self.w3.eth.block_number
            gas_price = self.w3.eth.gas_price
            
            return {
                'network': 'Sepolia Testnet',
                'chain_id': 11155111,
                'latest_block': latest_block,
                'gas_price': gas_price,
                'gas_price_gwei': self.w3.from_wei(gas_price, 'gwei'),
                'connected': self.w3.is_connected(),
                'account_address': self.address
            }
        except Exception as e:
            return {
                'error': str(e),
                'connected': False
            }