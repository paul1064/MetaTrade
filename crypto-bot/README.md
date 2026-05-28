# 🚀 Crypto Trading Swap Bot

## Overview
An automated crypto trading bot that scans for emerging tokens on **Ethereum (Uniswap V3)** and **Solana (Jupiter)**, scores them by momentum, allocates capital with weighted distribution, and prepares swap transactions for manual confirmation via MetaMask/Phantom wallets.

### Key Features
- 🔍 **Emerging Token Discovery**: Identifies new tokens (<24h old) with unusual volume/liquidity spikes
- 📊 **Momentum Scoring Algorithm**: Creative scoring based on volume surge, liquidity depth, buy pressure, price momentum, and token age
- 💰 **Weighted Allocation**: Distributes 8 USDC units across top positions (higher scores = larger allocations)
- 🎯 **Risk Management**: Fixed 40% Stop Loss, +150% Take Profit with 50% partial exit
- 🤝 **Manual Confirmation**: You control all transactions - bot prepares, you execute via wallet UI

---

## Architecture

| Component | Description |
|-----------|-------------|
| **Language** | Python 3.x (easiest on Linux Lite - pre-installed or `sudo apt install python3`) |
| **Deployment** | Local execution via terminal |
| **Confirmation** | Manual (bot prepares transactions, you confirm in MetaMask/Phantom) |
| **Chains** | Ethereum (Uniswap V3) & Solana (Jupiter) |
| **Capital** | 8 USDC total, max 8 positions |

### Strategy Parameters
```json
{
  "total_usdc_units": 8,
  "max_positions": 8,
  "take_profit_percent": 150,
  "stop_loss_percent": 40,
  "tp_partial_exit_percent": 50,
  "token_max_age_hours": 24,
  "min_liquidity_usd": 50000,
  "min_volume_24h_usd": 100000
}
```

---

## What is an RPC Endpoint?

An **RPC (Remote Procedure Call) endpoint** is a URL that allows your bot to communicate with blockchain nodes. Think of it as an API gateway to read blockchain data (prices, liquidity, volumes) and send transactions.

### Free RPC Endpoints (Ready to Use)

**Ethereum:**
- `https://eth.llamarpc.com` ⭐ (default in config)
- `https://rpc.ankr.com/ethereum`
- Get your own (higher rate limits): [Alchemy](https://alchemy.com) or [Infura](https://infura.io)

**Solana:**
- `https://api.mainnet-beta.solana.com` ⭐ (default in config)
- `https://solana-api.projectserum.com`
- Get your own: [QuickNode](https://quicknode.com)

> 💡 **Tip**: The default config already includes working free RPC endpoints. You can start immediately without changes!

---

## Installation Steps

### Step 1: Navigate to Bot Directory
```bash
cd /workspace/crypto-bot
```

### Step 2: Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

**Dependencies include:**
- `web3` - Ethereum blockchain interaction
- `solana` - Solana blockchain interaction  
- `requests` - API calls to Jupiter, Uniswap
- `numpy` - Mathematical calculations for scoring
- `pandas` - Data manipulation
- `python-dateutil` - Date/time utilities

### Step 3: Verify Installation
```bash
python3 -c "from scanner import TokenScanner; print('✅ Installation successful!')"
```

### Step 4: (Optional) Customize Configuration
Edit `config.json` if you want to:
- Change RPC endpoints
- Adjust strategy parameters (TP/SL percentages, min liquidity, etc.)
- Modify token age filters

```bash
nano config.json
```

---

## How to Run the Bot

### Quick Start (Single Scan)
```bash
cd /workspace/crypto-bot
python3 main.py
```

Then select option **1** for a single scan cycle.

### Continuous Mode (Auto-scan every 15 minutes)
```bash
python3 main.py
```
Then select option **2** for continuous scanning.

### Custom Interval Mode
```bash
python3 main.py
```
Then select option **3** and enter your preferred interval in minutes.

---

## How It Works (Step-by-Step)

### 1️⃣ Scanner (`scanner.py`)
Discovers emerging tokens by scanning:
- **Ethereum**: New Uniswap V3 pools with tokens <24h old
- **Solana**: New Jupiter-listed tokens with momentum

**Demo Mode**: Currently uses curated demo tokens for demonstration. For production, integrate with:
- Ethereum: Uniswap Subgraph, DexScreener API, or Birdeye API
- Solana: Jupiter API, Solscan API, or DexScreener

### 2️⃣ Scorer (`scorer.py`)
Calculates momentum score (0-100) using creative algorithm:

| Factor | Weight | Description |
|--------|--------|-------------|
| Volume Surge | 25% | How much volume exceeds minimum threshold |
| Liquidity Depth | 20% | Higher liquidity = more stable |
| Buy Pressure | 20% | Ratio of buys to total transactions |
| Price Momentum | 20% | 24h price change (positive preferred) |
| Age Bonus | 15% | Newer tokens get slight boost |

### 3️⃣ Allocator (`allocator.py`)
Distributes 8 USDC units with **weighted distribution**:
- Top-scored tokens receive larger allocations
- Minimum 0.5 USDC per position for diversification
- Calculates entry price, TP, SL levels for each position

### 4️⃣ Transaction Builder (`transaction_builder.py`)
Prepares ready-to-execute swap transactions:
- **Ethereum**: Generates Uniswap V3 swap URLs
- **Solana**: Fetches optimal routes from Jupiter API
- Includes slippage tolerance, TP/SL price levels
- Provides step-by-step execution instructions

### 5️⃣ Output
Bot displays:
- Top momentum tokens with scores
- Allocation report (how much USDC per token)
- Transaction URLs for manual execution
- Saves results to timestamped JSON file

---

## Example Output

```
================================================================================
  CRYPTO TRADING SWAP BOT
  Emerging Token Scanner for Ethereum & Solana
================================================================================

🚀 Initializing Crypto Trading Bot...
================================================================================
✅ Configuration loaded
   Total USDC Units: 8
   Max Positions: 8
   Take Profit: +150%
   Stop Loss: -40%
   TP Partial Exit: 50%
   Token Max Age: 24 hours
   Min Liquidity: $50,000
   Min Volume 24h: $100,000
================================================================================

📌 SELECT MODE:
   1. Run once (single scan)
   2. Continuous mode (scan every 15 min)
   3. Custom interval

Enter choice (1/2/3): 1

⏰ Scan Cycle Started: 2024-01-15 14:30:00
--------------------------------------------------------------------------------

📡 STEP 1: Scanning for emerging tokens...
🔍 Scanning Ethereum for emerging tokens...
   Found 3 Ethereum tokens
🔍 Scanning Solana for emerging tokens...
   Found 4 Solana tokens
✅ Found 7 potential tokens (3 ETH, 4 SOL)

📊 STEP 2: Scoring tokens by momentum...

   Top 5 Momentum Scores:
   #1 MEW (SOL): 83.12/100
   #2 WIF (SOL): 80.81/100
   #3 POPCAT (SOL): 78.43/100
   #4 WOJAK (ETH): 75.20/100
   #5 TURBO (ETH): 72.15/100

💰 STEP 3: Calculating weighted allocations...

================================================================================
POSITION ALLOCATION REPORT
================================================================================
Total USDC Units: 8
Number of Positions: 7

#1 - MEW (SOL)
    Address: UfT6gALJVDK8dvNvH9cMvjKfGbcAMKCDqPxXqKpump
    Momentum Score: 83.12/100
    Allocation: 1.5 USDC (18.75%)
    Entry Price: $0.0028
    Take Profit: $0.007 (+150%)
      → Partial Exit (50%): 0.75 USDC at TP
    Stop Loss: $0.00168 (-40%)

#2 - WIF (SOL)
    Address: EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm
    Momentum Score: 80.81/100
    Allocation: 1.45 USDC (18.13%)
    ...

--------------------------------------------------------------------------------
Total Allocated: 8.0 USDC
Remaining: 0.0 USDC
================================================================================

📝 STEP 4: Preparing transactions for manual execution...

================================================================================
TRANSACTION PREPARATION REPORT
================================================================================

📝 Transaction #1
   Chain: ETHEREUM
   DEX: Uniswap V3
   Action: BUY PEPE
   Amount: 1.2 USDC
   Slippage: 2.0%
   Take Profit: $0.000003075
   Stop Loss: $0.000000738

   🔗 Execute: https://app.uniswap.org/swap/?inputCurrency=0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48&outputCurrency=0x6982508145454Ce325dDbE47a25d4ec3d2311933&exactAmount=1.2&chain=ethereum

   📋 Instructions:
      1. Open the URL in your browser with MetaMask installed
      2. Connect your wallet
      3. Review the swap details
      4. Click 'Swap' and confirm in MetaMask
      5. Save the transaction hash for tracking
--------------------------------------------------------------------------------

✅ Scan cycle completed!
   Results saved to: scan_results_20240115_143000.json
```

---

## File Structure

```
crypto-bot/
├── main.py                  # Main entry point - orchestrates all components
├── scanner.py               # Token discovery logic (ETH + SOL)
├── scorer.py                # Momentum scoring algorithm
├── allocator.py             # Position sizing & weighted distribution
├── transaction_builder.py   # Prepares Uniswap V3 & Jupiter swaps
├── config.json              # RPC endpoints & strategy parameters
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── scan_results_*.json      # Generated output files (timestamped)
```

---

## Safety Notes ⚠️

| Risk | Mitigation |
|------|------------|
| **Never share private keys** | Bot only prepares transactions - keys never leave your wallet |
| **Test with small amounts first** | Start with minimum allocations to verify workflow |
| **New tokens are extremely high risk** | Rug pulls common in <24h tokens - only risk what you can lose |
| **You control all confirmations** | Manual confirmation prevents unauthorized transactions |
| **Slippage on volatile tokens** | 2% slippage tolerance set - adjust in config if needed |

### Best Practices
1. ✅ Always verify token contracts before swapping (use Etherscan/Solscan)
2. ✅ Check liquidity locks and team tokens
3. ✅ Set price alerts for TP/SL levels
4. ✅ Keep transaction records for tax purposes
5. ✅ Never FOMO into tokens after massive pumps

---

## Troubleshooting

### "Module not found" Error
```bash
pip3 install -r requirements.txt --upgrade
```

### "RPC connection failed" Error
- Try alternative RPC endpoints in `config.json`
- Public RPCs have rate limits - consider getting your own from Alchemy/QuickNode

### "No tokens found" Message
- Demo mode uses static data - in production, integrate real APIs
- Adjust `min_liquidity_usd` and `min_volume_24h_usd` in config to be less restrictive

### Jupiter API Timeout (Solana)
- Network congestion common on Solana
- Bot has fallback URL generation - transactions will still work

---

## Future Enhancements

- [ ] Real-time API integration (DexScreener, Birdeye, Uniswap Subgraph)
- [ ] Telegram/Discord alerts for high-score tokens
- [ ] Automated TP/SL monitoring with notifications
- [ ] Backtesting module for strategy optimization
- [ ] Multi-wallet support
- [ ] Gas price optimization for Ethereum

---

## Support & Disclaimer

**This bot is for educational purposes only.** Cryptocurrency trading involves substantial risk of loss. Always do your own research (DYOR) before trading.

- Past performance does not guarantee future results
- New/emerging tokens are extremely volatile
- Only trade with funds you can afford to lose
- Consult a financial advisor if unsure

---

**Happy Trading! 🚀** Remember: The goal is consistent profits, not home runs. Manage risk carefully.
