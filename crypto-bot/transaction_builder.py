"""
Transaction Builder - Prepares swap transactions for Uniswap V3 (ETH) and Jupiter (SOL)
Output: Transaction data ready for manual confirmation in MetaMask/Phantom
"""

import json
import requests
from typing import Dict, Any, Optional


class TransactionBuilder:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.eth_config = config['ethereum']
        self.sol_config = config['solana']
        self.strategy = config['strategy']
    
    def build_uniswap_v3_swap(self, token: Dict[str, Any], amount_usdc: float, user_address: str) -> Optional[Dict[str, Any]]:
        """
        Build Uniswap V3 swap transaction data for Ethereum.
        
        Note: This prepares the transaction parameters. User must confirm in MetaMask.
        For actual execution, use the Uniswap Interface or construct calldata with web3.py.
        """
        
        try:
            # Uniswap V3 Router address
            router_address = self.eth_config['uniswap_v3_router']
            usdc_address = self.eth_config['usdc_address']
            token_address = token['address']
            
            # Calculate slippage tolerance (2% for volatile tokens)
            slippage_bps = 200  # 2%
            
            # Prepare transaction parameters
            tx_data = {
                'chain': 'ethereum',
                'dex': 'Uniswap V3',
                'token_symbol': token['symbol'],
                'token_address': token_address,
                'action': 'BUY',
                'input_token': 'USDC',
                'input_amount': amount_usdc,
                'output_token': token['symbol'],
                'slippage_tolerance': f"{slippage_bps / 100}%",
                'take_profit_price': token['take_profit_price'],
                'stop_loss_price': token['stop_loss_price'],
                'tp_partial_exit_units': token['tp_partial_exit_units'],
            }
            
            # Generate Uniswap URL for easy execution
            # Format: https://app.uniswap.org/swap?inputCurrency=USDC&outputCurrency=TOKEN&amount=AMOUNT
            uniswap_url = (
                f"https://app.uniswap.org/swap/"
                f"?inputCurrency={usdc_address}"
                f"&outputCurrency={token_address}"
                f"&exactAmount={amount_usdc}"
                f"&chain=ethereum"
            )
            
            tx_data['execution_url'] = uniswap_url
            tx_data['instructions'] = (
                f"1. Open the URL in your browser with MetaMask installed\n"
                f"2. Connect your wallet\n"
                f"3. Review the swap details\n"
                f"4. Click 'Swap' and confirm in MetaMask\n"
                f"5. Save the transaction hash for tracking"
            )
            
            return tx_data
            
        except Exception as e:
            print(f"❌ Error building Uniswap V3 transaction: {e}")
            return None
    
    def build_jupiter_swap(self, token: Dict[str, Any], amount_usdc: float, user_wallet: str) -> Optional[Dict[str, Any]]:
        """
        Build Jupiter swap transaction for Solana.
        
        Uses Jupiter Quote API to get optimal route, then prepares transaction.
        """
        
        try:
            usdc_mint = self.sol_config['usdc_mint']
            token_mint = token['address']
            jupiter_api = self.sol_config['jupiter_api']
            
            # Convert USDC amount to lamports (USDC has 6 decimals on Solana)
            amount = int(amount_usdc * 1_000_000)  # 6 decimals
            
            # Get quote from Jupiter API
            quote_url = f"{jupiter_api}/quote"
            params = {
                'inputMint': usdc_mint,
                'outputMint': token_mint,
                'amount': amount,
                'slippageBps': 200,  # 2% slippage
                'onlyDirectRoutes': False,
            }
            
            response = requests.get(quote_url, params=params, timeout=10)
            quote_data = response.json()
            
            if 'error' in quote_data:
                print(f"Jupiter API error: {quote_data['error']}")
                # Fall back to manual URL generation
                out_amount = 0
                price_impact = 0
            else:
                out_amount = quote_data.get('outAmount', 0)
                price_impact = quote_data.get('priceImpactPct', 0)
            
            # Generate Jupiter URL for execution
            jupiter_url = (
                f"https://jup.ag/swap/"
                f"{usdc_mint}-{token_mint}"
                f"?amount={amount_usdc}"
                f"&slippage=2"
            )
            
            tx_data = {
                'chain': 'solana',
                'dex': 'Jupiter',
                'token_symbol': token['symbol'],
                'token_address': token_mint,
                'action': 'BUY',
                'input_token': 'USDC',
                'input_amount': amount_usdc,
                'estimated_output': out_amount,
                'price_impact': f"{float(price_impact) * 100:.2f}%" if price_impact else "Unknown",
                'slippage_tolerance': "2%",
                'take_profit_price': token['take_profit_price'],
                'stop_loss_price': token['stop_loss_price'],
                'tp_partial_exit_units': token['tp_partial_exit_units'],
                'execution_url': jupiter_url,
                'instructions': (
                    f"1. Open the URL in your browser with Phantom wallet installed\n"
                    f"2. Connect your wallet\n"
                    f"3. Review the swap route and details\n"
                    f"4. Click 'Swap' and confirm in Phantom\n"
                    f"5. Save the transaction signature for tracking"
                )
            }
            
            return tx_data
            
        except Exception as e:
            print(f"❌ Error building Jupiter transaction: {e}")
            # Return fallback with manual URL
            token_mint = token['address']
            usdc_mint = self.sol_config['usdc_mint']
            
            jupiter_url = f"https://jup.ag/swap/{usdc_mint}-{token_mint}?amount={amount_usdc}&slippage=2"
            
            return {
                'chain': 'solana',
                'dex': 'Jupiter',
                'token_symbol': token['symbol'],
                'token_address': token_mint,
                'action': 'BUY',
                'input_token': 'USDC',
                'input_amount': amount_usdc,
                'execution_url': jupiter_url,
                'instructions': (
                    f"1. Open the URL in your browser with Phantom wallet\n"
                    f"2. Connect wallet and review swap\n"
                    f"3. Confirm transaction"
                )
            }
    
    def build_exit_transaction(self, token: Dict[str, Any], exit_type: str, 
                                units_to_sell: float, user_address: str) -> Optional[Dict[str, Any]]:
        """
        Build exit transaction (sell) for taking profit or cutting loss.
        
        exit_type: 'TP_PARTIAL', 'TP_FULL', or 'SL'
        """
        
        if token['chain'] == 'ethereum':
            return self._build_uniswap_exit(token, exit_type, units_to_sell, user_address)
        elif token['chain'] == 'solana':
            return self._build_jupiter_exit(token, exit_type, units_to_sell, user_address)
        else:
            return None
    
    def _build_uniswap_exit(self, token: Dict[str, Any], exit_type: str, 
                            units_to_sell: float, user_address: str) -> Dict[str, Any]:
        """Build Uniswap V3 sell transaction."""
        
        token_address = token['address']
        usdc_address = self.eth_config['usdc_address']
        
        uniswap_url = (
            f"https://app.uniswap.org/swap/"
            f"?inputCurrency={token_address}"
            f"&outputCurrency={usdc_address}"
            f"&exactAmount={units_to_sell}"
            f"&chain=ethereum"
        )
        
        exit_reasons = {
            'TP_PARTIAL': f"Take Profit (50% exit) at +{self.strategy['take_profit_percent']}%",
            'TP_FULL': f"Take Profit (Full exit) at +{self.strategy['take_profit_percent']}%",
            'SL': f"Stop Loss at -{self.strategy['stop_loss_percent']}%"
        }
        
        return {
            'chain': 'ethereum',
            'dex': 'Uniswap V3',
            'token_symbol': token['symbol'],
            'action': 'SELL',
            'exit_type': exit_reasons.get(exit_type, exit_type),
            'output_amount_usdc': units_to_sell,
            'execution_url': uniswap_url,
            'instructions': (
                f"1. Open URL in browser with MetaMask\n"
                f"2. Connect wallet\n"
                f"3. Review and confirm swap"
            )
        }
    
    def _build_jupiter_exit(self, token: Dict[str, Any], exit_type: str,
                            units_to_sell: float, user_address: str) -> Dict[str, Any]:
        """Build Jupiter sell transaction."""
        
        token_mint = token['address']
        usdc_mint = self.sol_config['usdc_mint']
        
        jupiter_url = (
            f"https://jup.ag/swap/"
            f"{token_mint}-{usdc_mint}"
            f"?amount={units_to_sell}"
            f"&slippage=2"
        )
        
        exit_reasons = {
            'TP_PARTIAL': f"Take Profit (50% exit) at +{self.strategy['take_profit_percent']}%",
            'TP_FULL': f"Take Profit (Full exit) at +{self.strategy['take_profit_percent']}%",
            'SL': f"Stop Loss at -{self.strategy['stop_loss_percent']}%"
        }
        
        return {
            'chain': 'solana',
            'dex': 'Jupiter',
            'token_symbol': token['symbol'],
            'action': 'SELL',
            'exit_type': exit_reasons.get(exit_type, exit_type),
            'output_amount_usdc': units_to_sell,
            'execution_url': jupiter_url,
            'instructions': (
                f"1. Open URL in browser with Phantom\n"
                f"2. Connect wallet\n"
                f"3. Review and confirm swap"
            )
        }
    
    def generate_transaction_report(self, transactions: list) -> str:
        """Generate a formatted report of all prepared transactions."""
        
        if not transactions:
            return "No transactions to report."
        
        report = []
        report.append("\n" + "="*80)
        report.append("TRANSACTION PREPARATION REPORT")
        report.append("="*80)
        
        for i, tx in enumerate(transactions, 1):
            report.append(f"\n📝 Transaction #{i}")
            report.append(f"   Chain: {tx['chain'].upper()}")
            report.append(f"   DEX: {tx['dex']}")
            report.append(f"   Action: {tx['action']} {tx['token_symbol']}")
            report.append(f"   Amount: {tx['input_amount']} USDC")
            
            if 'estimated_output' in tx:
                report.append(f"   Est. Output: {tx['estimated_output']} {tx['token_symbol']}")
            
            if 'price_impact' in tx:
                report.append(f"   Price Impact: {tx['price_impact']}")
            
            report.append(f"   Slippage: {tx['slippage_tolerance']}")
            report.append(f"   Take Profit: ${tx['take_profit_price']}")
            report.append(f"   Stop Loss: ${tx['stop_loss_price']}")
            report.append(f"\n   🔗 Execute: {tx['execution_url']}")
            report.append(f"\n   📋 Instructions:\n      {tx['instructions']}")
            report.append("-"*80)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Test transaction builder
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    builder = TransactionBuilder(config)
    
    # Sample token data
    sample_token_eth = {
        'chain': 'ethereum',
        'symbol': 'ROCKET',
        'address': '0x456...',
        'price_usd': 0.001,
        'take_profit_price': 0.0025,
        'stop_loss_price': 0.0006,
        'tp_partial_exit_units': 1.0
    }
    
    sample_token_sol = {
        'chain': 'solana',
        'symbol': 'MOON',
        'address': 'ABC...',
        'price_usd': 0.05,
        'take_profit_price': 0.125,
        'stop_loss_price': 0.03,
        'tp_partial_exit_units': 0.75
    }
    
    print("\n=== ETHEREUM TRANSACTION ===")
    eth_tx = builder.build_uniswap_v3_swap(sample_token_eth, 2.5, "0xUserAddress...")
    if eth_tx:
        print(f"Token: {eth_tx['token_symbol']}")
        print(f"Amount: {eth_tx['input_amount']} USDC")
        print(f"Execute: {eth_tx['execution_url']}")
    
    print("\n=== SOLANA TRANSACTION ===")
    sol_tx = builder.build_jupiter_swap(sample_token_sol, 1.5, "UserWallet...")
    if sol_tx:
        print(f"Token: {sol_tx['token_symbol']}")
        print(f"Amount: {sol_tx['input_amount']} USDC")
        print(f"Execute: {sol_tx['execution_url']}")
