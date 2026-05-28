"""
Position Allocator - Distributes USDC units with weighted distribution
Top-scored tokens receive larger allocations
"""

import numpy as np
from typing import List, Dict, Any


class PositionAllocator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.strategy = config['strategy']
        self.total_units = self.strategy['total_usdc_units']
        self.max_positions = self.strategy['max_positions']
    
    def calculate_weighted_allocation(self, scored_tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Allocate USDC units using weighted distribution based on momentum scores.
        
        Method: 
        1. Take top N tokens (up to max_positions)
        2. Calculate weight for each based on normalized score
        3. Distribute total_units proportionally
        4. Ensure minimum 0.5 units per position for diversification
        """
        
        if not scored_tokens:
            return []
        
        # Take top tokens up to max_positions
        top_tokens = scored_tokens[:self.max_positions]
        
        if len(top_tokens) == 0:
            return []
        
        # Extract scores
        scores = np.array([t['momentum_score'] for t in top_tokens])
        
        # Handle edge case where all scores are 0
        if scores.sum() == 0:
            # Equal distribution if no scores
            base_allocation = self.total_units / len(top_tokens)
            for token in top_tokens:
                token['allocation_units'] = round(base_allocation, 2)
                token['allocation_percent'] = round(100 / len(top_tokens), 2)
            return top_tokens
        
        # Calculate weights (proportional to score)
        weights = scores / scores.sum()
        
        # Calculate raw allocations
        raw_allocations = weights * self.total_units
        
        # Apply minimum allocation constraint (0.5 units minimum)
        min_units = 0.5
        final_allocations = []
        remaining_units = self.total_units
        
        # First pass: apply minimum and track remaining
        for i, token in enumerate(top_tokens):
            allocated = max(min_units, raw_allocations[i])
            # Don't exceed remaining units
            allocated = min(allocated, remaining_units - (len(top_tokens) - i - 1) * min_units)
            allocated = max(allocated, min_units) if remaining_units > min_units else remaining_units
            
            final_allocations.append(round(allocated, 2))
            remaining_units -= allocated
        
        # Second pass: distribute any remaining units proportionally to top scorers
        if remaining_units > 0.01:
            # Add remaining to top scorer(s)
            for i in range(len(final_allocations)):
                if remaining_units <= 0:
                    break
                add_amount = min(remaining_units, 0.5)  # Max 0.5 extra per token
                final_allocations[i] = round(final_allocations[i] + add_amount, 2)
                remaining_units -= add_amount
        
        # Assign allocations to tokens
        for i, token in enumerate(top_tokens):
            token['allocation_units'] = final_allocations[i]
            token['allocation_percent'] = round((final_allocations[i] / self.total_units) * 100, 2)
            token['entry_price'] = token['price_usd']
            token['take_profit_price'] = round(token['price_usd'] * (1 + self.strategy['take_profit_percent'] / 100), 8)
            token['stop_loss_price'] = round(token['price_usd'] * (1 - self.strategy['stop_loss_percent'] / 100), 8)
            token['tp_partial_exit_units'] = round(token['allocation_units'] * self.strategy['tp_partial_exit_percent'] / 100, 2)
        
        return top_tokens
    
    def generate_allocation_report(self, allocated_tokens: List[Dict[str, Any]]) -> str:
        """Generate a human-readable allocation report."""
        
        if not allocated_tokens:
            return "No tokens to allocate."
        
        report = []
        report.append("\n" + "="*80)
        report.append("POSITION ALLOCATION REPORT")
        report.append("="*80)
        report.append(f"Total USDC Units: {self.total_units}")
        report.append(f"Number of Positions: {len(allocated_tokens)}")
        report.append("")
        
        total_allocated = 0
        for i, token in enumerate(allocated_tokens, 1):
            report.append(f"#{i} - {token['symbol']} ({token['chain'].upper()})")
            report.append(f"    Address: {token['address']}")
            report.append(f"    Momentum Score: {token['momentum_score']}/100")
            report.append(f"    Allocation: {token['allocation_units']} USDC ({token['allocation_percent']}%)")
            report.append(f"    Entry Price: ${token['entry_price']}")
            report.append(f"    Take Profit: ${token['take_profit_price']} (+{self.strategy['take_profit_percent']}%)")
            report.append(f"      → Partial Exit (50%): {token['tp_partial_exit_units']} USDC at TP")
            report.append(f"    Stop Loss: ${token['stop_loss_price']} (-{self.strategy['stop_loss_percent']}%)")
            report.append("")
            total_allocated += token['allocation_units']
        
        report.append("-"*80)
        report.append(f"Total Allocated: {round(total_allocated, 2)} USDC")
        report.append(f"Remaining: {round(self.total_units - total_allocated, 2)} USDC")
        report.append("="*80)
        
        return "\n".join(report)


if __name__ == "__main__":
    import json
    
    # Test allocator with sample scored data
    sample_tokens = [
        {'symbol': 'ROCKET', 'chain': 'ethereum', 'address': '0x456...', 'momentum_score': 92.5, 'price_usd': 0.001},
        {'symbol': 'PEPE2', 'chain': 'ethereum', 'address': '0x123...', 'momentum_score': 78.3, 'price_usd': 0.0001},
        {'symbol': 'MOON', 'chain': 'solana', 'address': 'ABC...', 'momentum_score': 65.1, 'price_usd': 0.05},
        {'symbol': 'GEM', 'chain': 'solana', 'address': 'DEF...', 'momentum_score': 55.0, 'price_usd': 0.02},
    ]
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    allocator = PositionAllocator(config)
    allocated = allocator.calculate_weighted_allocation(sample_tokens)
    
    print(allocator.generate_allocation_report(allocated))
