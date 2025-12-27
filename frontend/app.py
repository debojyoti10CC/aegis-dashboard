#!/usr/bin/env python3
"""
Simple Flask server for Disaster Management System Frontend
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import sys
import asyncio
import json
from datetime import datetime

# Add parent directory to path to import disaster management system
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from disaster_management_system.agents.watchtower import WatchtowerAgent
    from disaster_management_system.agents.auditor import AuditorAgent
    from disaster_management_system.agents.treasurer import TreasurerAgent
    from disaster_management_system.shared.logging_config import setup_logging
    SYSTEM_AVAILABLE = True
except ImportError:
    SYSTEM_AVAILABLE = False
    print("Warning: Disaster management system not available, using mock data")

app = Flask(__name__, static_folder='.', template_folder='.')

# Global variables for agents
watchtower = None
auditor = None
treasurer = None

def initialize_agents():
    """Initialize disaster management agents"""
    global watchtower, auditor, treasurer
    
    if not SYSTEM_AVAILABLE:
        return False
    
    try:
        setup_logging()
        
        # Agent configurations
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
        
        treasurer_config = {
            'heartbeat_interval': 30,
            'min_funding_amount': 0.001,
            'max_funding_amount': 0.01,
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
        auditor = AuditorAgent(auditor_config)
        treasurer = TreasurerAgent(treasurer_config)
        
        return True
        
    except Exception as e:
        print(f"Error initializing agents: {e}")
        return False

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/api/status')
def get_status():
    """Get system status"""
    try:
        if not SYSTEM_AVAILABLE:
            return jsonify({
                'blockchain': {
                    'status': 'connected',
                    'network': 'Sepolia Testnet',
                    'address': '0x5D3f355f0EA186896802878E7Aa0b184469c3033',
                    'balance': '0.0486'
                },
                'agents': {
                    'watchtower': {'status': 'online', 'processed': 0},
                    'auditor': {'status': 'online', 'verified': 0},
                    'treasurer': {'status': 'online', 'transactions': 0}
                }
            })
        
        # Get real status from agents
        blockchain_status = 'offline'
        balance = '0.0000'
        address = 'Not connected'
        
        if treasurer and treasurer.blockchain:
            try:
                connected = asyncio.run(treasurer.blockchain.connect())
                if connected:
                    blockchain_status = 'connected'
                    address = treasurer.blockchain.address
                    balance = str(asyncio.run(treasurer.blockchain.get_balance()))
            except:
                pass
        
        return jsonify({
            'blockchain': {
                'status': blockchain_status,
                'network': 'Sepolia Testnet',
                'address': address,
                'balance': balance
            },
            'agents': {
                'watchtower': {'status': 'online' if watchtower else 'offline'},
                'auditor': {'status': 'online' if auditor else 'offline'},
                'treasurer': {'status': 'online' if treasurer else 'offline'}
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-disaster', methods=['POST'])
@limiter.limit("10 per minute")  # Limit AI processing
def test_disaster():
    """Test disaster detection"""
    try:
        if not SYSTEM_AVAILABLE or not watchtower:
            # Return mock data
            return jsonify({
                'status': 'success',
                'disaster_type': 'CASUALTY',
                'confidence': 100,
                'severity': 0.22,
                'coordinates': '(34.0522, -118.2437)'
            })
        
        # Check if image file exists
        image_path = '../test_images/intense_fire.jpg'
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Files in parent directory: {os.listdir('..')}")
            return jsonify({'status': 'error', 'error': f'Image file not found: {image_path}'})
        
        print(f"Processing image: {image_path}")
        
        # Run real disaster detection
        result = asyncio.run(watchtower.process_test_image(image_path, (34.0522, -118.2437)))
        
        print(f"Detection result: {result}")
        
        if result:
            return jsonify({
                'status': 'success',
                'disaster_type': result.disaster_type.upper(),
                'confidence': int(result.confidence * 100),
                'severity': result.severity_score,
                'coordinates': f"({result.location[0]}, {result.location[1]})"
            })
        else:
            return jsonify({'status': 'no_disaster'})
            
    except Exception as e:
        print(f"Error in test_disaster: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/full-test', methods=['POST'])
@limiter.limit("3 per minute")  # Limit expensive blockchain operations
def full_test():
    """Run full system test"""
    try:
        if not SYSTEM_AVAILABLE:
            # Return mock data
            return jsonify({
                'status': 'success',
                'steps': {
                    'detection': {
                        'disaster_type': 'CASUALTY',
                        'confidence': 100,
                        'severity': 0.22
                    },
                    'verification': {
                        'score': 65,
                        'human_impact': 117,
                        'funding_recommendation': 0.001
                    },
                    'transaction': {
                        'tx_hash': '0xd997b0488c4f84298e538a648ad5e72fec943fb9e1c4a8d0a0b07d1508889e3e',
                        'amount': 0.001,
                        'recipients': 3,
                        'status': 'confirmed'
                    }
                }
            })
        
        # Run real full test
        # Step 1: Disaster Detection
        disaster_result = asyncio.run(watchtower.process_test_image('../test_images/intense_fire.jpg', (34.0522, -118.2437)))
        
        if not disaster_result:
            return jsonify({'status': 'no_disaster'})
        
        # Step 2: Verification
        verified_result = asyncio.run(auditor.verify_disaster(disaster_result))
        
        if not verified_result or verified_result.verification_score < 60:
            return jsonify({'status': 'verification_failed'})
        
        # Step 3: Funding
        funding_transaction = asyncio.run(treasurer.distribute_funding(verified_result))
        
        if not funding_transaction:
            return jsonify({'status': 'funding_failed'})
        
        return jsonify({
            'status': 'success',
            'steps': {
                'detection': {
                    'disaster_type': disaster_result.disaster_type.upper(),
                    'confidence': int(disaster_result.confidence * 100),
                    'severity': disaster_result.severity_score
                },
                'verification': {
                    'score': verified_result.verification_score,
                    'human_impact': verified_result.human_impact_estimate,
                    'funding_recommendation': verified_result.funding_recommendation
                },
                'transaction': {
                    'tx_hash': funding_transaction.transaction_hashes[0] if funding_transaction.transaction_hashes else 'pending',
                    'amount': funding_transaction.total_amount,
                    'recipients': len(funding_transaction.recipient_addresses),
                    'status': funding_transaction.status
                }
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    try:
        # For now, return mock stats
        # In a real implementation, you'd query your database
        return jsonify({
            'disasters_detected': 5,
            'verified_events': 3,
            'total_funding': 0.015,
            'transactions': 8,
            'success_rate': 85.7
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for load balancers"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'system_available': SYSTEM_AVAILABLE,
            'agents_initialized': watchtower is not None and auditor is not None and treasurer is not None
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚨 Starting Disaster Management System Frontend...")
    print("=" * 60)
    
    # Initialize agents
    if initialize_agents():
        print("✅ Disaster management agents initialized")
    else:
        print("⚠️  Running in demo mode (agents not available)")
    
    print(f"🌐 Frontend available at: http://localhost:5000")
    print(f"📱 Mobile friendly interface")
    print(f"🔄 Real-time disaster management simulation")
    print("=" * 60)
    
    # Production vs Development
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(debug=debug, host='0.0.0.0', port=port)