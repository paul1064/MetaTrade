# Crypto Trading Swap Bot - Setup Guide

## Overview
This bot scans for emerging tokens on Ethereum (Uniswap V3) and Solana (Jupiter), calculates weighted allocations, and prepares swap transactions for manual confirmation via MetaMask/Phantom.

## Architecture
- **Language**: Python (easiest on Linux Lite, pre-installed or simple `apt install python3`)
- **Deployment**: Local execution via terminal
- **Confirmation**: Manual (bot prepares transactions, you confirm in wallet)
- **Strategy**: 
  - Scans new pools/tokens by age (<24h), volume surge, liquidity growth
  - Weighted allocation based on momentum score
  - Fixed 40% SL, partial TP at +150% (50% position), remainder with trailing stop

## What is an RPC Endpoint?
An **RPC (Remote Procedure Call) endpoint** is a URL that allows your bot to communicate with blockchain nodes. Think of it as an API gateway to read blockchain data and send transactions.

### Free RPC Endpoints to Use:
**Ethereum:**
- Public: `https://eth.llamarpc.com`
- Public: `https://rpc.ankr.com/ethereum`
- Get your own (higher limits): [Alchemy](https://alchemy.com) or [Infura](https://infura.io)

**Solana:**
- Public: `https://api.mainnet-beta.solana.com`
- Public: `https://solana-api.projectserum.com`
- Get your own: [QuickNode](https://quicknode.com)

## Installation Steps

### 1. Install Python Dependencies
```bash
cd /workspace/crypto-bot
pip3 install -r requirements.txt
```

### 2. Configure RPC Endpoints
Edit `config.json` with your preferred RPC URLs (free ones work for starting).

### 3. Run the Bot
```bash
python3 main.py
```

## How It Works
1. **Scanner**: Finds new tokens (<24h old) with unusual volume/liquidity spikes
2. **Scorer**: Ranks tokens by momentum (volume change, liquidity depth, social mentions if available)
3. **Allocator**: Distributes 8 USDC units with weighted distribution (top scores get more)
4. **Transaction Builder**: Creates calibrated swap transactions with TP/SL levels
5. **Output**: Displays transaction details for you to execute manually in MetaMask/Phantom

## Files Included
- `main.py` - Main execution loop
- `scanner.py` - Token discovery logic
- `scorer.py` - Momentum scoring algorithm
- `allocator.py` - Position sizing logic
- `transaction_builder.py` - Prepares Uniswap V3 & Jupiter swaps
- `config.json` - RPC endpoints and parameters
- `requirements.txt` - Python dependencies

## Safety Notes
- ⚠️ **Never share your private keys** - this bot only prepares transactions
- ⚠️ Test with small amounts first
- ⚠️ New tokens are extremely high risk (rug pulls common)
- ⚠️ You control all confirmations manually
