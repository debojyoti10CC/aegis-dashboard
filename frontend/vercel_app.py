#!/usr/bin/env python3
"""
Vercel-optimized Flask server for Disaster Management System Frontend
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import sys
import asyncio
import json
from datetime import datetime
import logging

# Vercel-specific configuration
app = Flask(__name__, static_folder='.', template_folder='.')

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per hour"]
)

# For Vercel, we'll use mock data since the full system is too large
SYSTEM_AVAILABLE = False

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
        return jsonify({
            'blockchain': {
                'status': 'connected',
                'network': 'Sepolia Testnet (Demo)',
                'address': '0x5D3f355f0EA186896802878E7Aa0b184469c3033',
                'balance': '0.0486'
            },
            'agents': {
                'watchtower': {'status': 'online'},
                'auditor': {'status': 'online'},
                'treasurer': {'status': 'online'}
            },
            'mode': 'vercel_demo',
            'note': 'This is a demo version running on Vercel. For real transactions, deploy with Docker or Heroku.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-disaster', methods=['POST'])
@limiter.limit("10 per minute")
def test_disaster():
    """Test disaster detection (demo version)"""
    try:
        # Return mock data for Vercel demo
        import random
        
        disaster_types = ['FIRE', 'FLOOD', 'EARTHQUAKE', 'CASUALTY']
        disaster_type = random.choice(disaster_types)
        confidence = random.randint(85, 100)
        severity = round(random.uniform(0.1, 0.9), 2)
        
        return jsonify({
            'status': 'success',
            'disaster_type': disaster_type,
            'confidence': confidence,
            'severity': severity,
            'coordinates': '(34.0522, -118.2437)',
            'note': 'Demo mode - no real AI processing on Vercel'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/full-test', methods=['POST'])
@limiter.limit("3 per minute")
def full_test():
    """Run full system test (demo version)"""
    try:
        import random
        
        # Simulate the full process with mock data
        disaster_type = random.choice(['FIRE', 'FLOOD', 'EARTHQUAKE', 'CASUALTY'])
        confidence = random.randint(85, 100)
        severity = round(random.uniform(0.1, 0.9), 2)
        verification_score = random.randint(60, 95)
        human_impact = random.randint(50, 500)
        funding_amount = round(random.uniform(0.001, 0.01), 3)
        
        # Generate mock transaction hash
        tx_hash = '0x' + ''.join(random.choices('0123456789abcdef', k=64))
        
        return jsonify({
            'status': 'success',
            'steps': {
                'detection': {
                    'disaster_type': disaster_type,
                    'confidence': confidence,
                    'severity': severity
                },
                'verification': {
                    'score': verification_score,
                    'human_impact': human_impact,
                    'funding_recommendation': funding_amount
                },
                'transaction': {
                    'tx_hash': tx_hash,
                    'amount': funding_amount,
                    'recipients': 3,
                    'status': 'simulated'
                }
            },
            'note': 'Demo mode - no real blockchain transactions on Vercel'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get system statistics (demo)"""
    try:
        import random
        
        return jsonify({
            'disasters_detected': random.randint(10, 50),
            'verified_events': random.randint(5, 25),
            'total_funding': round(random.uniform(0.1, 1.0), 3),
            'transactions': random.randint(15, 75),
            'success_rate': round(random.uniform(80, 95), 1),
            'note': 'Demo statistics for Vercel deployment'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Vercel"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0-vercel',
        'platform': 'vercel',
        'mode': 'demo'
    })

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(debug=True)