#!/usr/bin/env python3
from web3 import Web3
from eth_account import Account

# Connect to Sepolia
w3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/1df86dfd23a442cc8609f6dbe66d5832'))
account = Account.from_key('0x847888bebc95f4ec43485b92093ae632e211c0d2a59d2ebf19a874c00a22144c')

print(f"Connected: {w3.is_connected()}")
print(f"Address: {account.address}")

balance = w3.eth.get_balance(account.address)
balance_eth = w3.from_wei(balance, 'ether')
print(f"Balance: {balance_eth} ETH")

if balance_eth == 0:
    print("\n❌ NO TESTNET ETH FOUND!")
    print("You need to get testnet ETH from a faucet:")
    print("1. Go to https://sepoliafaucet.com/")
    print("2. Enter your address:", account.address)
    print("3. Request testnet ETH")
else:
    print(f"✅ You have {balance_eth} ETH for transactions")