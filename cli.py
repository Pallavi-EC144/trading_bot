#!/usr/bin/env python3
"""
Trading Bot CLI - Binance Futures Testnet
"""

import os
import sys
import click
from dotenv import load_dotenv
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from bot.logging_config import setup_logging
from bot.client import BinanceFuturesClient
from bot.orders import OrderManager
from bot.validators import OrderValidator

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

class TradingBotCLI:
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = None
        self.order_manager = None
        
    def initialize(self):
        """Initialize the trading bot"""
        if not self.api_key or not self.api_secret:
            logger.error("API credentials not found. Please set BINANCE_API_KEY and BINANCE_API_SECRET in .env file")
            return False
        
        try:
            self.client = BinanceFuturesClient(self.api_key, self.api_secret)
            self.order_manager = OrderManager(self.client)
            
            # Test connection
            account = self.client.get_account_info()
            logger.info(f"Connected to Binance Futures Testnet successfully!")
            logger.info(f"Account balance available")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False
    
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
        """Place an order"""
        try:
            logger.info(f"Processing {order_type} order...")
            
            if order_type.upper() == 'MARKET':
                order = self.order_manager.place_market_order(symbol, side, quantity)
            else:  # LIMIT
                if not price:
                    raise ValueError("Price is required for LIMIT orders")
                order = self.order_manager.place_limit_order(symbol, side, quantity, price)
            
            # Display order details
            click.echo("\n" + self.order_manager.format_order_response(order))
            
            if order.get('status') == 'FILLED':
                click.echo("✅ Order executed successfully!")
            elif order.get('status') == 'NEW':
                click.echo("✅ Order placed successfully and waiting for execution!")
            else:
                click.echo(f"ℹ️ Order status: {order.get('status')}")
            
            logger.info(f"Order placed successfully: {order.get('orderId')}")
            
        except ValueError as e:
            click.echo(f"❌ Validation Error: {e}", err=True)
            logger.error(f"Validation error: {e}")
        except Exception as e:
            click.echo(f"❌ Failed to place order: {e}", err=True)
            logger.error(f"Order placement failed: {e}")

@click.command()
@click.option('--symbol', prompt='Symbol', help='Trading symbol (e.g., BTCUSDT)')
@click.option('--side', type=click.Choice(['BUY', 'SELL'], case_sensitive=False), prompt='Side', help='BUY or SELL')
@click.option('--order-type', type=click.Choice(['MARKET', 'LIMIT'], case_sensitive=False), prompt='Order type', help='MARKET or LIMIT')
@click.option('--quantity', type=float, prompt='Quantity', help='Order quantity')
@click.option('--price', type=float, help='Price for LIMIT orders (required for LIMIT)')
def main(symbol, side, order_type, quantity, price):
    """Trading Bot - Place orders on Binance Futures Testnet"""
    
    # Header
    click.echo("\n" + "=" * 60)
    click.echo("🚀 PRIMETRADE.AI - Trading Bot (Binance Futures Testnet)")
    click.echo("=" * 60 + "\n")
    
    # Validate price for limit orders
    if order_type.upper() == 'LIMIT' and price is None:
        click.echo("❌ Price is required for LIMIT orders", err=True)
        sys.exit(1)
    
    # Initialize bot
    bot = TradingBotCLI()
    if not bot.initialize():
        click.echo("❌ Failed to initialize trading bot. Check logs for details.", err=True)
        sys.exit(1)
    
    # Place order
    bot.place_order(symbol.upper(), side.upper(), order_type.upper(), quantity, price)

if __name__ == '__main__':
    main()
