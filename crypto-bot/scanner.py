"""
Token Scanner - Discovers emerging tokens on Ethereum and Solana
Uses demo data for demonstration (real API integration requires premium services)
"""

from typing import List, Dict, Any


class TokenScanner:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.eth_config = config['ethereum']
        self.sol_config = config['solana']
        self.strategy = config['strategy']
    
    def scan_ethereum(self) -> List[Dict[str, Any]]:
        """Demo: Ethereum tokens with momentum"""
        print("🔍 Scanning Ethereum for emerging tokens...")
        
        demo_tokens = [
            {
                'chain': 'ethereum', 'symbol': 'PEPE',
                'address': '0x6982508145454Ce325dDbE47a25d4ec3d2311933',
                'name': 'Pepe', 'price_usd': 0.00000123,
                'liquidity_usd': 2500000, 'volume_24h': 15000000,
                'price_change_24h': 45.5, 'buys_24h': 5200, 'sells_24h': 3100,
                'dex': 'Uniswap V3', 'age_hours': 18
            },
            {
                'chain': 'ethereum', 'symbol': 'TURBO',
                'address': '0xA35923162C49cF95e6BF26623385eb431ad920D3',
                'name': 'Turbo', 'price_usd': 0.0045,
                'liquidity_usd': 850000, 'volume_24h': 3200000,
                'price_change_24h': 78.2, 'buys_24h': 2100, 'sells_24h': 890,
                'dex': 'Uniswap V3', 'age_hours': 8
            },
            {
                'chain': 'ethereum', 'symbol': 'WOJAK',
                'address': '0x5026F006B85729a8b14553FAE6af249aD16c9aaB',
                'name': 'Wojak', 'price_usd': 0.000089,
                'liquidity_usd': 420000, 'volume_24h': 1800000,
                'price_change_24h': 120.5, 'buys_24h': 1800, 'sells_24h': 650,
                'dex': 'Uniswap V3', 'age_hours': 12
            }
        ]
        print(f"   Found {len(demo_tokens)} Ethereum tokens")
        return demo_tokens
    
    def scan_solana(self) -> List[Dict[str, Any]]:
        """Demo: Solana tokens with momentum"""
        print("🔍 Scanning Solana for emerging tokens...")
        
        demo_tokens = [
            {
                'chain': 'solana', 'symbol': 'BONK',
                'address': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
                'name': 'Bonk', 'price_usd': 0.000012,
                'liquidity_usd': 5200000, 'volume_24h': 28000000,
                'price_change_24h': 35.8, 'buys_24h': 8500, 'sells_24h': 5200,
                'dex': 'Jupiter', 'age_hours': 6
            },
            {
                'chain': 'solana', 'symbol': 'WIF',
                'address': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',
                'name': 'dogwifhat', 'price_usd': 1.85,
                'liquidity_usd': 3800000, 'volume_24h': 22000000,
                'price_change_24h': 62.3, 'buys_24h': 6200, 'sells_24h': 2800,
                'dex': 'Jupiter', 'age_hours': 10
            },
            {
                'chain': 'solana', 'symbol': 'POPCAT',
                'address': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr',
                'name': 'Popcat', 'price_usd': 0.35,
                'liquidity_usd': 1200000, 'volume_24h': 8500000,
                'price_change_24h': 95.2, 'buys_24h': 3500, 'sells_24h': 1200,
                'dex': 'Jupiter', 'age_hours': 15
            },
            {
                'chain': 'solana', 'symbol': 'MEW',
                'address': 'UfT6gALJVDK8dvNvH9cMvjKfGbcAMKCDqPxXqKpump',
                'name': 'Cat in a dogs world', 'price_usd': 0.0028,
                'liquidity_usd': 980000, 'volume_24h': 5200000,
                'price_change_24h': 110.5, 'buys_24h': 2800, 'sells_24h': 950,
                'dex': 'Jupiter', 'age_hours': 4
            }
        ]
        print(f"   Found {len(demo_tokens)} Solana tokens")
        return demo_tokens
    
    def scan_all(self) -> List[Dict[str, Any]]:
        """Scan both chains"""
        eth_tokens = self.scan_ethereum()
        sol_tokens = self.scan_solana()
        all_tokens = eth_tokens + sol_tokens
        print(f"✅ Found {len(all_tokens)} potential tokens ({len(eth_tokens)} ETH, {len(sol_tokens)} SOL)")
        return all_tokens


if __name__ == "__main__":
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    scanner = TokenScanner(config)
    tokens = scanner.scan_all()
    print("\n" + "="*60)
    for t in tokens:
        print(f"{t['symbol']} ({t['chain'].upper()}): +{t['price_change_24h']}% | Vol: ${t['volume_24h']:,}")
