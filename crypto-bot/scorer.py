"""
Momentum Scorer - Ranks tokens by potential using creative scoring algorithm
Factors: Volume surge, liquidity depth, buy/sell ratio, price momentum, token age
"""

import numpy as np
from typing import List, Dict, Any


class MomentumScorer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.strategy = config['strategy']
    
    def calculate_score(self, token: Dict[str, Any]) -> float:
        """
        Calculate momentum score for a token (0-100 scale).
        
        Creative scoring factors:
        1. Volume Surge Score (25%): How much volume exceeds minimum threshold
        2. Liquidity Depth Score (20%): Higher liquidity = more stable
        3. Buy Pressure Score (20%): Ratio of buys to total transactions
        4. Price Momentum Score (20%): 24h price change (positive preferred)
        5. Age Bonus Score (15%): Newer tokens get slight boost
        """
        
        # 1. Volume Surge Score (0-25 points)
        min_volume = self.strategy['min_volume_24h_usd']
        volume_ratio = token['volume_24h'] / min_volume
        # Logarithmic scaling to prevent extreme values
        volume_score = min(25, np.log1p(volume_ratio) * 5)
        
        # 2. Liquidity Depth Score (0-20 points)
        min_liquidity = self.strategy['min_liquidity_usd']
        liquidity_ratio = token['liquidity_usd'] / min_liquidity
        liquidity_score = min(20, np.log1p(liquidity_ratio) * 4)
        
        # 3. Buy Pressure Score (0-20 points)
        total_txns = token['buys_24h'] + token['sells_24h']
        if total_txns > 0:
            buy_ratio = token['buys_24h'] / total_txns
            # Score higher when buys dominate (0.7+ ratio = max score)
            buy_score = min(20, buy_ratio * 25)
        else:
            buy_score = 0
        
        # 4. Price Momentum Score (-20 to +20 points)
        price_change = token['price_change_24h']
        # Positive changes rewarded, negative penalized
        # Cap at +/- 20 points
        momentum_score = np.clip(price_change / 5, -20, 20)
        
        # 5. Age Bonus Score (0-15 points)
        # Newer tokens get higher scores (within our <24h window)
        max_age = self.strategy['token_max_age_hours']
        age_hours = token['age_hours']
        if age_hours > 0:
            # Tokens <6 hours old get max bonus, then linearly decrease
            age_score = max(0, 15 * (1 - (age_hours / max_age)))
        else:
            age_score = 15
        
        # Calculate weighted total
        total_score = (
            volume_score + 
            liquidity_score + 
            buy_score + 
            momentum_score + 
            age_score
        )
        
        # Normalize to 0-100 scale
        normalized_score = np.clip(total_score, 0, 100)
        
        return round(normalized_score, 2)
    
    def score_all_tokens(self, tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add momentum scores to all tokens and sort by score descending."""
        scored_tokens = []
        
        for token in tokens:
            token_copy = token.copy()
            token_copy['momentum_score'] = self.calculate_score(token)
            scored_tokens.append(token_copy)
        
        # Sort by momentum score (highest first)
        scored_tokens.sort(key=lambda x: x['momentum_score'], reverse=True)
        
        return scored_tokens
    
    def get_top_tokens(self, tokens: List[Dict[str, Any]], limit: int = None) -> List[Dict[str, Any]]:
        """Get top N tokens by momentum score."""
        if limit is None:
            limit = self.strategy['max_positions']
        
        scored = self.score_all_tokens(tokens)
        return scored[:limit]


if __name__ == "__main__":
    import json
    
    # Test scorer with sample data
    sample_tokens = [
        {
            'chain': 'ethereum',
            'symbol': 'PEPE2',
            'address': '0x123...',
            'price_usd': 0.0001,
            'liquidity_usd': 100000,
            'volume_24h': 500000,
            'price_change_24h': 45.5,
            'buys_24h': 1200,
            'sells_24h': 800,
            'age_hours': 6
        },
        {
            'chain': 'solana',
            'symbol': 'MOON',
            'address': 'ABC...',
            'price_usd': 0.05,
            'liquidity_usd': 75000,
            'volume_24h': 200000,
            'price_change_24h': -10.2,
            'buys_24h': 500,
            'sells_24h': 700,
            'age_hours': 12
        },
        {
            'chain': 'ethereum',
            'symbol': 'ROCKET',
            'address': '0x456...',
            'price_usd': 0.001,
            'liquidity_usd': 200000,
            'volume_24h': 1000000,
            'price_change_24h': 120.0,
            'buys_24h': 2000,
            'sells_24h': 500,
            'age_hours': 3
        }
    ]
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    scorer = MomentumScorer(config)
    scored = scorer.score_all_tokens(sample_tokens)
    
    print("TOKEN MOMENTUM SCORES:")
    print("="*80)
    
    for token in scored:
        print(f"\n{token['symbol']} ({token['chain'].upper()})")
        print(f"  Momentum Score: {token['momentum_score']}/100")
        print(f"  Volume 24h: ${token['volume_24h']:,}")
        print(f"  Liquidity: ${token['liquidity_usd']:,}")
        print(f"  Price Change: {token['price_change_24h']:+.2f}%")
        print(f"  Buy/Sell Ratio: {token['buys_24h']}/{token['sells_24h']}")
        print(f"  Age: {token['age_hours']}h")
