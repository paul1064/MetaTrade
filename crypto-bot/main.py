#!/usr/bin/env python3
"""
Crypto Trading Swap Bot - Main Entry Point
Scans for emerging tokens, scores them, allocates positions, and prepares transactions.

Usage: python3 main.py
"""

import json
import time
from datetime import datetime
from scanner import TokenScanner
from scorer import MomentumScorer
from allocator import PositionAllocator
from transaction_builder import TransactionBuilder


class CryptoTradingBot:
    def __init__(self, config_path: str = 'config.json'):
        """Initialize the trading bot with configuration."""
        
        print("🚀 Initializing Crypto Trading Bot...")
        print("="*80)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.strategy = self.config['strategy']
        
        # Initialize components
        self.scanner = TokenScanner(self.config)
        self.scorer = MomentumScorer(self.config)
        self.allocator = PositionAllocator(self.config)
        self.tx_builder = TransactionBuilder(self.config)
        
        print(f"✅ Configuration loaded")
        print(f"   Total USDC Units: {self.strategy['total_usdc_units']}")
        print(f"   Max Positions: {self.strategy['max_positions']}")
        print(f"   Take Profit: +{self.strategy['take_profit_percent']}%")
        print(f"   Stop Loss: -{self.strategy['stop_loss_percent']}%")
        print(f"   TP Partial Exit: {self.strategy['tp_partial_exit_percent']}%")
        print(f"   Token Max Age: {self.strategy['token_max_age_hours']} hours")
        print(f"   Min Liquidity: ${self.strategy['min_liquidity_usd']:,}")
        print(f"   Min Volume 24h: ${self.strategy['min_volume_24h_usd']:,}")
        print("="*80)
    
    def run_scan_cycle(self):
        """Execute one complete scan-score-allocate-build cycle."""
        
        print(f"\n⏰ Scan Cycle Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*80)
        
        # Step 1: Scan for emerging tokens
        print("\n📡 STEP 1: Scanning for emerging tokens...")
        discovered_tokens = self.scanner.scan_all()
        
        if not discovered_tokens:
            print("⚠️  No tokens found matching criteria. Try again later.")
            return []
        
        # Step 2: Score tokens by momentum
        print("\n📊 STEP 2: Scoring tokens by momentum...")
        scored_tokens = self.scorer.score_all_tokens(discovered_tokens)
        
        # Show top 5 scores
        print("\n   Top 5 Momentum Scores:")
        for i, token in enumerate(scored_tokens[:5], 1):
            print(f"   #{i} {token['symbol']} ({token['chain'].upper()}): {token['momentum_score']}/100")
        
        # Step 3: Allocate positions
        print("\n💰 STEP 3: Calculating weighted allocations...")
        allocated_tokens = self.allocator.calculate_weighted_allocation(scored_tokens)
        
        # Print allocation report
        print(self.allocator.generate_allocation_report(allocated_tokens))
        
        # Step 4: Build transactions
        print("\n📝 STEP 4: Preparing transactions for manual execution...")
        transactions = []
        
        for token in allocated_tokens:
            if token['chain'] == 'ethereum':
                tx = self.tx_builder.build_uniswap_v3_swap(
                    token, 
                    token['allocation_units'], 
                    "YOUR_ETH_ADDRESS"  # Replace with actual address
                )
            elif token['chain'] == 'solana':
                tx = self.tx_builder.build_jupiter_swap(
                    token,
                    token['allocation_units'],
                    "YOUR_SOL_WALLET"  # Replace with actual wallet
                )
            
            if tx:
                transactions.append(tx)
        
        # Print transaction report
        print(self.tx_builder.generate_transaction_report(transactions))
        
        # Save results to file
        self._save_results(allocated_tokens, transactions)
        
        print("\n✅ Scan cycle completed!")
        print(f"   Results saved to: scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        return allocated_tokens
    
    def _save_results(self, allocated_tokens: list, transactions: list):
        """Save scan results to JSON file."""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"scan_results_{timestamp}.json"
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'strategy': self.strategy,
            'allocated_tokens': allocated_tokens,
            'transactions_summary': [
                {
                    'chain': tx['chain'],
                    'dex': tx['dex'],
                    'token': tx['token_symbol'],
                    'action': tx['action'],
                    'amount_usdc': tx['input_amount'],
                    'execution_url': tx['execution_url']
                }
                for tx in transactions
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
    
    def run_continuous(self, interval_minutes: int = 15):
        """Run continuous scanning at specified intervals."""
        
        print(f"\n🔄 Starting continuous mode (scanning every {interval_minutes} minutes)...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_scan_cycle()
                
                next_run = datetime.now().timestamp() + (interval_minutes * 60)
                print(f"\n⏳ Next scan in {interval_minutes} minutes ({datetime.fromtimestamp(next_run).strftime('%H:%M:%S')})")
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n\n⛔ Stopped by user")
    
    def run_once(self):
        """Run a single scan cycle."""
        return self.run_scan_cycle()


def main():
    """Main entry point."""
    
    print("\n" + "="*80)
    print("  CRYPTO TRADING SWAP BOT")
    print("  Emerging Token Scanner for Ethereum & Solana")
    print("="*80)
    
    # Initialize bot
    bot = CryptoTradingBot()
    
    # Run mode selection
    print("\n\n📌 SELECT MODE:")
    print("   1. Run once (single scan)")
    print("   2. Continuous mode (scan every 15 min)")
    print("   3. Custom interval")
    
    try:
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == '1':
            bot.run_once()
        elif choice == '2':
            bot.run_continuous(interval_minutes=15)
        elif choice == '3':
            interval = int(input("Enter scan interval in minutes: ").strip())
            bot.run_continuous(interval_minutes=interval)
        else:
            print("Invalid choice. Running single scan by default.")
            bot.run_once()
            
    except KeyboardInterrupt:
        print("\n\n⛔ Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your configuration and try again.")
    
    print("\n👋 Good luck with your trades! Remember to manage risk carefully.")


if __name__ == "__main__":
    main()
