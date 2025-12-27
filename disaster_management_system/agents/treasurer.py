"""
Treasurer Agent - Blockchain Funding Distribution
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..shared.base_agent import BaseAgent
from ..shared.models import VerifiedEvent, FundingTransaction
from ..shared.blockchain import BlockchainManager


class TreasurerAgent(BaseAgent):
    """Agent responsible for blockchain funding distribution"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("treasurer", config)
        
        # Initialize blockchain manager
        blockchain_config = config.get('blockchain', {})
        self.blockchain = BlockchainManager(blockchain_config)
        
        # Funding configuration
        self.min_funding_amount = config.get('min_funding_amount', 0.01)  # ETH
        self.max_funding_amount = config.get('max_funding_amount', 2.0)   # ETH
        self.funding_timeout = config.get('funding_timeout', 300)  # seconds
        
        # Transaction tracking
        self.pending_transactions = {}
        self.completed_transactions = {}
        
    async def start(self):
        """Start the treasurer agent"""
        # Connect to blockchain first
        connected = await self.blockchain.connect()
        if not connected:
            self.logger.error("Failed to connect to blockchain - agent cannot start")
            return
        
        # Start the base agent
        await super().start()
    
    async def _processing_loop(self):
        """Main processing loop for funding distribution"""
        self.logger.info("Treasurer agent processing loop started")
        
        while self.is_running:
            try:
                # Process new verified events
                messages = await self.receive_messages()
                
                for message in messages:
                    await self.process_message(message.payload)
                
                # Check pending transaction statuses
                await self._check_pending_transactions()
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(5)
    
    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming verified disaster event"""
        try:
            if 'verified_event' in message:
                verified_event = VerifiedEvent.from_dict(message['verified_event'])
                funding_transaction = await self.distribute_funding(verified_event)
                
                if funding_transaction:
                    self.logger.info(f"Funding initiated for event {verified_event.event_id}: "
                                   f"{funding_transaction.total_amount} ETH")
                    
                    return {
                        'status': 'funding_initiated',
                        'transaction_id': funding_transaction.transaction_id,
                        'total_amount': funding_transaction.total_amount
                    }
                else:
                    self.logger.warning(f"Failed to initiate funding for event {verified_event.event_id}")
                    return {'status': 'funding_failed'}
            
            return {'status': 'no_event_to_fund'}
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def distribute_funding(self, verified_event: VerifiedEvent) -> Optional[FundingTransaction]:
        """Distribute funding based on verified disaster event"""
        try:
            # Calculate funding amount
            funding_amount = self._calculate_funding_amount(verified_event)
            
            if funding_amount < self.min_funding_amount:
                self.logger.info(f"Funding amount {funding_amount} below minimum threshold")
                return None
            
            # Check account balance
            balance = await self.blockchain.get_balance()
            if balance < funding_amount:
                self.logger.error(f"Insufficient balance: {balance} ETH, needed: {funding_amount} ETH")
                return None
            
            # Get recipient addresses
            recipients = self._get_recipients(verified_event)
            recipient_amounts = self.blockchain.calculate_recipient_amounts(funding_amount, recipients)
            
            # Execute transactions
            transaction_results = await self.blockchain.send_multiple_transactions(recipient_amounts)
            
            # Create funding transaction record
            funding_transaction = FundingTransaction(
                transaction_id="",  # Will be auto-generated
                event_id=verified_event.event_id,
                recipient_addresses=[r['address'] for r in recipient_amounts],
                amounts=[r['amount'] for r in recipient_amounts],
                transaction_hashes=[r.get('transaction_hash', '') for r in transaction_results],
                total_amount=funding_amount,
                status='pending',
                timestamp=datetime.utcnow()
            )
            
            # Store in pending transactions for monitoring
            self.pending_transactions[funding_transaction.transaction_id] = {
                'funding_transaction': funding_transaction,
                'transaction_results': transaction_results,
                'created_at': datetime.utcnow()
            }
            
            return funding_transaction
            
        except Exception as e:
            self.logger.error(f"Error distributing funding: {e}")
            return None
    
    def _calculate_funding_amount(self, verified_event: VerifiedEvent) -> float:
        """Calculate funding amount based on verified event"""
        try:
            # Start with the recommended amount from auditor
            base_amount = verified_event.funding_recommendation
            
            # Adjust based on verification score
            verification_factor = verified_event.verification_score / 100.0
            
            # Adjust based on human impact
            impact_factor = min(2.0, verified_event.human_impact_estimate / 1000.0)
            
            # Adjust based on disaster type
            disaster_multipliers = {
                'fire': 1.0,
                'flood': 1.2,
                'structural': 1.1,
                'casualty': 1.5
            }
            
            disaster_type = verified_event.original_event.disaster_type
            disaster_factor = disaster_multipliers.get(disaster_type, 1.0)
            
            # Calculate final amount
            final_amount = base_amount * verification_factor * impact_factor * disaster_factor
            
            # Apply min/max limits
            final_amount = max(self.min_funding_amount, min(self.max_funding_amount, final_amount))
            
            return round(final_amount, 4)  # Round to 4 decimal places
            
        except Exception as e:
            self.logger.error(f"Error calculating funding amount: {e}")
            return self.min_funding_amount
    
    def _get_recipients(self, verified_event: VerifiedEvent) -> List[Dict[str, Any]]:
        """Get recipient addresses and percentages based on disaster type"""
        disaster_type = verified_event.original_event.disaster_type
        return self.blockchain.get_default_recipients(disaster_type)
    
    async def _check_pending_transactions(self):
        """Check status of pending transactions"""
        completed_ids = []
        
        for tx_id, tx_data in self.pending_transactions.items():
            try:
                funding_transaction = tx_data['funding_transaction']
                transaction_results = tx_data['transaction_results']
                
                # Check each transaction hash
                all_confirmed = True
                any_failed = False
                
                for i, result in enumerate(transaction_results):
                    if 'transaction_hash' in result:
                        tx_hash = result['transaction_hash']
                        status = await self.blockchain.get_transaction_status(tx_hash)
                        
                        if status['status'] == 'confirmed':
                            continue
                        elif status['status'] == 'failed':
                            any_failed = True
                            break
                        else:
                            all_confirmed = False
                
                # Update transaction status
                if any_failed:
                    funding_transaction.status = 'failed'
                    completed_ids.append(tx_id)
                    self.logger.error(f"Transaction {tx_id} failed")
                elif all_confirmed:
                    funding_transaction.status = 'confirmed'
                    completed_ids.append(tx_id)
                    self.logger.info(f"Transaction {tx_id} confirmed")
                
                # Check for timeout
                time_elapsed = (datetime.utcnow() - tx_data['created_at']).total_seconds()
                if time_elapsed > self.funding_timeout:
                    funding_transaction.status = 'timeout'
                    completed_ids.append(tx_id)
                    self.logger.warning(f"Transaction {tx_id} timed out")
                
            except Exception as e:
                self.logger.error(f"Error checking transaction {tx_id}: {e}")
        
        # Move completed transactions
        for tx_id in completed_ids:
            if tx_id in self.pending_transactions:
                self.completed_transactions[tx_id] = self.pending_transactions.pop(tx_id)
    
    async def get_transaction_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific transaction"""
        try:
            # Check pending transactions
            if transaction_id in self.pending_transactions:
                tx_data = self.pending_transactions[transaction_id]
                funding_transaction = tx_data['funding_transaction']
                
                return {
                    'transaction_id': transaction_id,
                    'status': funding_transaction.status,
                    'total_amount': funding_transaction.total_amount,
                    'recipients': len(funding_transaction.recipient_addresses),
                    'created_at': funding_transaction.timestamp.isoformat()
                }
            
            # Check completed transactions
            if transaction_id in self.completed_transactions:
                tx_data = self.completed_transactions[transaction_id]
                funding_transaction = tx_data['funding_transaction']
                
                return {
                    'transaction_id': transaction_id,
                    'status': funding_transaction.status,
                    'total_amount': funding_transaction.total_amount,
                    'recipients': len(funding_transaction.recipient_addresses),
                    'created_at': funding_transaction.timestamp.isoformat(),
                    'transaction_hashes': funding_transaction.transaction_hashes
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting transaction status: {e}")
            return None
    
    async def get_funding_stats(self) -> Dict[str, Any]:
        """Get funding statistics"""
        try:
            total_pending = len(self.pending_transactions)
            total_completed = len(self.completed_transactions)
            
            # Calculate total amounts
            pending_amount = sum(
                tx_data['funding_transaction'].total_amount 
                for tx_data in self.pending_transactions.values()
            )
            
            completed_amount = sum(
                tx_data['funding_transaction'].total_amount 
                for tx_data in self.completed_transactions.values()
            )
            
            # Count by status
            status_counts = {'confirmed': 0, 'failed': 0, 'timeout': 0}
            for tx_data in self.completed_transactions.values():
                status = tx_data['funding_transaction'].status
                if status in status_counts:
                    status_counts[status] += 1
            
            # Get blockchain info
            network_info = self.blockchain.get_network_info()
            account_balance = await self.blockchain.get_balance()
            
            return {
                'pending_transactions': total_pending,
                'completed_transactions': total_completed,
                'pending_amount_eth': pending_amount,
                'completed_amount_eth': completed_amount,
                'total_amount_eth': pending_amount + completed_amount,
                'status_distribution': status_counts,
                'account_balance_eth': account_balance,
                'network_info': network_info,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting funding stats: {e}")
            return {}
    
    async def emergency_stop_funding(self) -> Dict[str, Any]:
        """Emergency stop for all funding operations"""
        try:
            self.logger.warning("Emergency stop activated - halting all funding operations")
            
            # Count pending transactions
            pending_count = len(self.pending_transactions)
            
            # Move all pending to completed with 'stopped' status
            for tx_id, tx_data in self.pending_transactions.items():
                tx_data['funding_transaction'].status = 'stopped'
                self.completed_transactions[tx_id] = tx_data
            
            self.pending_transactions.clear()
            
            return {
                'status': 'emergency_stop_activated',
                'stopped_transactions': pending_count,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in emergency stop: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def retry_failed_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Retry a failed transaction"""
        try:
            if transaction_id not in self.completed_transactions:
                return {'status': 'transaction_not_found'}
            
            tx_data = self.completed_transactions[transaction_id]
            funding_transaction = tx_data['funding_transaction']
            
            if funding_transaction.status != 'failed':
                return {'status': 'transaction_not_failed'}
            
            # Create new transaction with same parameters
            # This would require re-creating the verified event or storing more data
            self.logger.info(f"Retry requested for transaction {transaction_id}")
            
            return {'status': 'retry_not_implemented'}
            
        except Exception as e:
            self.logger.error(f"Error retrying transaction: {e}")
            return {'status': 'error', 'error': str(e)}