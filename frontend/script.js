class DisasterManagementUI {
    constructor() {
        this.stats = {
            disasters: 0,
            verified: 0,
            totalFunding: 0,
            transactions: 0
        };
        
        this.isBackendConnected = false;
        this.apiBase = window.location.origin;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkBackendConnection();
    }

    setupEventListeners() {
        document.getElementById('test-disaster-btn').addEventListener('click', () => {
            this.runRealDisasterTest();
        });

        document.getElementById('full-test-btn').addEventListener('click', () => {
            this.runRealFullSystemTest();
        });

        document.getElementById('clear-logs-btn').addEventListener('click', () => {
            this.clearLogs();
        });
    }

    async checkBackendConnection() {
        try {
            this.addLog('info', 'CHECKING BACKEND CONNECTION...');
            
            const response = await fetch(`${this.apiBase}/api/status`);
            if (response.ok) {
                const data = await response.json();
                this.isBackendConnected = true;
                
                // Update mode indicator
                const modeDisplay = document.getElementById('mode-display');
                const modeText = document.getElementById('mode-text');
                
                if (data.mode === 'vercel_demo') {
                    modeDisplay.className = 'mode-display demo-mode';
                    modeText.textContent = 'VERCEL DEMO MODE - SIMULATED TRANSACTIONS';
                    this.addLog('info', 'CONNECTED TO VERCEL DEMO SYSTEM');
                    this.addLog('warning', 'THIS IS A DEMO - NO REAL BLOCKCHAIN TRANSACTIONS');
                    this.addLog('info', 'FOR REAL TRANSACTIONS, USE DOCKER OR HEROKU DEPLOYMENT');
                } else {
                    modeDisplay.className = 'mode-display real-mode';
                    modeText.textContent = 'REAL TRANSACTION MODE ACTIVE';
                    // Show warning
                    document.getElementById('real-transaction-warning').style.display = 'block';
                    this.addLog('info', 'CONNECTED TO REAL DISASTER MANAGEMENT SYSTEM');
                    this.addLog('warning', 'REAL BLOCKCHAIN TRANSACTIONS ENABLED');
                    this.addLog('error', 'THIS WILL SPEND ACTUAL ETH FROM YOUR WALLET!');
                }
                
                // Update UI with status
                this.updateRealSystemStatus(data);
            } else {
                throw new Error('Backend not available');
            }
        } catch (error) {
            this.isBackendConnected = false;
            
            // Update mode indicator
            const modeDisplay = document.getElementById('mode-display');
            const modeText = document.getElementById('mode-text');
            modeDisplay.className = 'mode-display demo-mode';
            modeText.textContent = 'DEMO MODE - NO REAL TRANSACTIONS';
            
            this.addLog('warning', 'BACKEND NOT AVAILABLE - RUNNING IN DEMO MODE');
            this.addLog('info', 'RUN "PYTHON APP.PY" FOR REAL TRANSACTIONS');
            this.simulateSystemStartup();
        }
    }

    updateRealSystemStatus(data) {
        // Update blockchain status
        const status = data.blockchain.status === 'connected' ? 'connected' : 'error';
        this.updateBlockchainStatus(status, 
            status === 'connected' ? 
            `CONNECTED TO ${data.blockchain.network}` : 
            'BLOCKCHAIN CONNECTION FAILED'
        );
        
        if (data.blockchain.address && data.blockchain.balance) {
            this.updateWalletInfo(data.blockchain.address, data.blockchain.balance);
        }
        
        // Update agent statuses
        this.updateAgentStatus('watchtower', data.agents.watchtower.status === 'online');
        this.updateAgentStatus('auditor', data.agents.auditor.status === 'online');
        this.updateAgentStatus('treasurer', data.agents.treasurer.status === 'online');
        
        if (data.agents.watchtower.status === 'online' && 
            data.agents.auditor.status === 'online' && 
            data.agents.treasurer.status === 'online') {
            this.addLog('info', 'ALL AGENTS ONLINE AND READY FOR REAL TRANSACTIONS');
        }
    }

    simulateSystemStartup() {
        this.addLog('info', 'DEMO MODE - SIMULATED SYSTEM INITIALIZED');
        
        setTimeout(() => {
            this.updateBlockchainStatus('connecting', 'CONNECTING TO SEPOLIA TESTNET...');
        }, 1000);

        setTimeout(() => {
            this.updateBlockchainStatus('connected', 'CONNECTED TO SEPOLIA TESTNET (DEMO)');
            this.updateWalletInfo('0x5D3f355f0EA186896802878E7Aa0b184469c3033', '0.0486');
            this.updateAgentStatus('watchtower', true);
        }, 2000);

        setTimeout(() => {
            this.updateAgentStatus('auditor', true);
        }, 2500);

        setTimeout(() => {
            this.updateAgentStatus('treasurer', true);
            this.addLog('info', 'ALL AGENTS ONLINE (DEMO MODE)');
            this.addLog('warning', 'RUN "PYTHON APP.PY" FOR REAL TRANSACTIONS');
        }, 3000);
    }

    updateBlockchainStatus(status, message) {
        const statusElement = document.getElementById('blockchain-status');
        statusElement.className = `status-display ${status}`;
        statusElement.textContent = message;
    }

    updateWalletInfo(address, balance) {
        const walletInfo = document.getElementById('wallet-info');
        walletInfo.innerHTML = `
            <div>ADDRESS: ${address}</div>
            <div>BALANCE: ${balance} ETH</div>
        `;
    }

    updateAgentStatus(agentName, online) {
        const dot = document.getElementById(`${agentName}-dot`);
        if (dot) {
            dot.className = `agent-dot ${online ? 'online' : 'offline'}`;
        }
    }

    updateCardStatus(cardType, status, details) {
        const statusElement = document.getElementById(`${cardType}-status`);
        const detailsElement = document.getElementById(`${cardType}-details`);
        
        statusElement.className = `status-indicator ${status}`;
        statusElement.textContent = status.toUpperCase();
        detailsElement.textContent = details;
    }

    addLog(type, message) {
        const terminalContent = document.getElementById('terminal-content');
        const timestamp = new Date().toLocaleString();
        
        const logLine = document.createElement('div');
        logLine.className = `log-line ${type}`;
        logLine.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="log-text">${message}</span>
        `;
        
        terminalContent.appendChild(logLine);
        terminalContent.scrollTop = terminalContent.scrollHeight;
    }

    clearLogs() {
        const terminalContent = document.getElementById('terminal-content');
        terminalContent.innerHTML = '';
        this.addLog('info', 'SYSTEM LOGS CLEARED');
    }

    updateStats() {
        document.getElementById('disasters-count').textContent = this.stats.disasters;
        document.getElementById('verified-count').textContent = this.stats.verified;
        document.getElementById('total-funding').textContent = this.stats.totalFunding.toFixed(3);
        document.getElementById('transactions-count').textContent = this.stats.transactions;
    }

    async runRealDisasterTest() {
        if (!this.isBackendConnected) {
            this.addLog('error', 'BACKEND NOT CONNECTED - CANNOT RUN REAL TEST');
            return;
        }

        this.addLog('info', 'STARTING REAL DISASTER DETECTION TEST...');
        
        // Reset card statuses
        this.updateCardStatus('detect', 'processing', 'PROCESSING REAL TEST IMAGE...');
        this.updateCardStatus('verify', 'waiting', 'WAITING FOR DETECTION...');
        this.updateCardStatus('disburse', 'waiting', 'WAITING FOR VERIFICATION...');
        this.updateCardStatus('audit', 'waiting', 'WAITING FOR TRANSACTION...');

        try {
            const response = await fetch(`${this.apiBase}/api/test-disaster`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.updateCardStatus('detect', 'completed', 
                    `REAL DISASTER DETECTED: ${result.disaster_type} (${result.confidence}% CONFIDENCE)`);
                
                this.addLog('info', `REAL DISASTER DETECTED: ${result.disaster_type} (${result.confidence}% CONFIDENCE)`);
                this.stats.disasters++;
                this.updateStats();
            } else {
                this.updateCardStatus('detect', 'failed', 'NO DISASTER DETECTED OR ERROR OCCURRED');
                this.addLog('error', 'REAL DISASTER DETECTION FAILED');
            }
            
        } catch (error) {
            this.updateCardStatus('detect', 'failed', `ERROR: ${error.message}`);
            this.addLog('error', `REAL DISASTER TEST FAILED: ${error.message}`);
        }
    }

    async runRealFullSystemTest() {
        if (!this.isBackendConnected) {
            this.addLog('error', 'BACKEND NOT CONNECTED - CANNOT RUN REAL TEST');
            this.addLog('info', 'RUN "PYTHON APP.PY" TO ENABLE REAL TRANSACTIONS');
            return;
        }

        this.addLog('info', 'STARTING REAL FULL SYSTEM TEST...');
        this.addLog('error', 'THIS WILL MAKE ACTUAL BLOCKCHAIN TRANSACTIONS!');
        
        // Reset all card statuses
        this.updateCardStatus('detect', 'processing', 'PROCESSING REAL DISASTER DETECTION...');
        this.updateCardStatus('verify', 'waiting', 'WAITING FOR DETECTION...');
        this.updateCardStatus('disburse', 'waiting', 'WAITING FOR VERIFICATION...');
        this.updateCardStatus('audit', 'waiting', 'WAITING FOR TRANSACTION...');

        try {
            const response = await fetch(`${this.apiBase}/api/full-test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                const steps = result.steps;
                
                // Step 1: Detection Results
                this.updateCardStatus('detect', 'completed', 
                    `REAL DISASTER DETECTED: ${steps.detection.disaster_type} (${steps.detection.confidence}% CONFIDENCE)`);
                
                this.addLog('info', `REAL DISASTER DETECTED: ${steps.detection.disaster_type}`);
                this.stats.disasters++;
                
                await this.delay(1000);
                
                // Step 2: Verification Results
                this.updateCardStatus('verify', 'processing', 'RUNNING REAL DISASTER VERIFICATION...');
                this.addLog('info', 'RUNNING REAL DISASTER VERIFICATION...');
                
                await this.delay(2000);
                
                this.updateCardStatus('verify', 'completed', 
                    `REAL VERIFICATION PASSED: ${steps.verification.score}/100 - ${steps.verification.human_impact} PEOPLE AFFECTED`);
                
                this.addLog('info', `REAL VERIFICATION PASSED: ${steps.verification.score}/100`);
                this.stats.verified++;
                
                await this.delay(1000);
                
                // Step 3: Real Blockchain Transaction
                this.updateCardStatus('disburse', 'processing', 'EXECUTING REAL BLOCKCHAIN TRANSACTION...');
                this.addLog('error', 'EXECUTING REAL BLOCKCHAIN TRANSACTION...');
                this.addLog('error', 'SPENDING REAL ETH FROM YOUR WALLET!');
                
                await this.delay(3000);
                
                this.updateCardStatus('disburse', 'completed', 
                    `REAL TRANSACTION CONFIRMED! HASH: ${steps.transaction.tx_hash.substring(0, 10)}...`);
                
                this.updateCardStatus('audit', 'completed', 
                    `TRANSACTION RECORDED ON BLOCKCHAIN - FULLY AUDITABLE`);
                
                this.addLog('info', 'REAL BLOCKCHAIN TRANSACTION SUCCESSFUL!');
                this.addLog('info', `TRANSACTION HASH: ${steps.transaction.tx_hash}`);
                this.addLog('info', 'FUNDS ACTUALLY MOVED ON SEPOLIA TESTNET!');
                
                this.stats.totalFunding += steps.transaction.amount;
                this.stats.transactions++;
                this.updateStats();
                
                // Update wallet balance
                this.updateWalletBalance();
                
                this.addLog('info', 'REAL DISASTER MANAGEMENT SYSTEM TEST COMPLETED!');
                
            } else {
                this.addLog('error', `REAL SYSTEM TEST FAILED: ${result.status}`);
                if (result.error) {
                    this.addLog('error', `ERROR DETAILS: ${result.error}`);
                }
            }
            
        } catch (error) {
            this.addLog('error', `REAL SYSTEM TEST FAILED: ${error.message}`);
        }
    }

    async updateWalletBalance() {
        try {
            const response = await fetch(`${this.apiBase}/api/status`);
            if (response.ok) {
                const data = await response.json();
                if (data.blockchain.address && data.blockchain.balance) {
                    this.updateWalletInfo(data.blockchain.address, data.blockchain.balance);
                    this.addLog('info', `UPDATED BALANCE: ${data.blockchain.balance} ETH`);
                }
            }
        } catch (error) {
            console.error('Failed to update wallet balance:', error);
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the UI when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new DisasterManagementUI();
});