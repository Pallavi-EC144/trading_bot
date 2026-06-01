#!/usr/bin/env python3
"""
Professional Trading Bot CLI - Binance Futures Testnet
With Rich UI, Colors, and Enhanced Features
"""

import os
import sys
import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich import print as rprint
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Rich console for beautiful output
console = Console()

# Import bot modules
from bot.logging_config import setup_logging
from bot.client import BinanceFuturesClient
from bot.orders import OrderManager
from bot.validators import OrderValidator
from bot.exceptions import ValidationError, APIError, NetworkError

# Setup logging
logger = setup_logging()

class ProfessionalTradingBot:
    """Professional trading bot with enhanced UX"""
    
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = None
        self.order_manager = None
        
    def display_banner(self):
        """Display professional banner"""
        banner = Panel(
            "[bold cyan]🐂 Binance Futures Testnet Trading Bot[/bold cyan]\n"
            "[dim]Professional Trading Interface | Primetrade.ai[/dim]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(banner)
    
    def display_order_summary(self, symbol, side, order_type, quantity, price=None):
        """Display order summary before submission"""
        table = Table(title="📋 Order Summary", style="bold yellow")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Symbol", f"[bold]{symbol}[/bold]")
        
        # Color code BUY/SELL
        side_color = "green" if side == "BUY" else "red"
        table.add_row("Side", f"[{side_color}]{side}[/{side_color}]")
        
        table.add_row("Type", f"[yellow]{order_type}[/yellow]")
        table.add_row("Quantity", f"[bold]{quantity}[/bold]")
        
        if price:
            table.add_row("Price", f"[bold]${price:,.2f}[/bold]")
        
        console.print(table)
    
    def display_order_result(self, order):
        """Display order result beautifully"""
        if order.get('status') == 'FILLED':
            status_color = "green"
            status_icon = "✅"
        elif order.get('status') == 'NEW':
            status_color = "yellow"
            status_icon = "⏳"
        else:
            status_color = "red"
            status_icon = "❌"
        
        result_table = Table(title=f"{status_icon} Order Result", style=status_color)
        result_table.add_column("Field", style="cyan")
        result_table.add_column("Value", style="white")
        
        result_table.add_row("Order ID", str(order.get('orderId')))
        result_table.add_row("Status", f"[{status_color}]{order.get('status')}[/{status_color}]")
        result_table.add_row("Symbol", order.get('symbol'))
        result_table.add_row("Side", order.get('side'))
        result_table.add_row("Type", order.get('type'))
        result_table.add_row("Quantity", order.get('origQty'))
        
        if order.get('price') and float(order.get('price')) > 0:
            result_table.add_row("Price", f"${float(order.get('price')):,.2f}")
        
        if order.get('executedQty') and float(order.get('executedQty')) > 0:
            result_table.add_row("Executed", order.get('executedQty'))
        
        if order.get('avgPrice') and float(order.get('avgPrice')) > 0:
            result_table.add_row("Avg Price", f"${float(order.get('avgPrice')):,.2f}")
        
        console.print(result_table)
        
        # Show fancy animation for successful orders
        if order.get('status') == 'FILLED':
            console.print("\n[green]🎉 Order executed successfully![/green]\n")
        elif order.get('status') == 'NEW':
            console.print("\n[yellow]⏳ Order placed! Waiting for execution...[/yellow]\n")
    
    def check_balance(self):
        """Check and display account balance"""
        try:
            account = self.client.get_account_info()
            
            table = Table(title="💰 Account Balance", style="bold cyan")
            table.add_column("Asset", style="yellow")
            table.add_column("Wallet Balance", style="green")
            table.add_column("Available", style="white")
            
            for asset in account.get('assets', []):
                wallet_balance = float(asset.get('walletBalance', 0))
                available = float(asset.get('availableBalance', 0))
                
                if wallet_balance > 0:
                    table.add_row(
                        asset['asset'],
                        f"${wallet_balance:,.2f}",
                        f"${available:,.2f}"
                    )
            
            console.print(table)
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Failed to fetch balance: {e}[/red]")
            return False
    
    def initialize(self):
        """Initialize the trading bot"""
        if not self.api_key or not self.api_secret:
            console.print("[red]❌ API credentials not found![/red]")
            console.print("[yellow]Please create a .env file with:[/yellow]")
            console.print("  BINANCE_API_KEY=your_key")
            console.print("  BINANCE_API_SECRET=your_secret")
            return False
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Connecting to Binance...", total=None)
                self.client = BinanceFuturesClient(self.api_key, self.api_secret)
                self.order_manager = OrderManager(self.client)
                account = self.client.get_account_info()
                progress.update(task, completed=True)
            
            console.print("[green]✅ Connected to Binance Futures Testnet successfully![/green]")
            
            # Show welcome info
            console.print(f"[dim]Account Type: Futures Testnet[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Failed to initialize: {e}[/red]")
            logger.error(f"Initialization failed: {e}")
            return False
    
    def place_order(self, symbol, side, order_type, quantity, price=None):
        """Place an order with professional error handling"""
        try:
            # Display summary
            self.display_order_summary(symbol, side, order_type, quantity, price)
            
            # Confirm with user
            if not Confirm.ask("\n[bold]Proceed with order?[/bold]"):
                console.print("[yellow]Order cancelled[/yellow]")
                return None
            
            # Place order with progress indicator
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Submitting order...", total=None)
                
                if order_type.upper() == 'MARKET':
                    order = self.order_manager.place_market_order(symbol, side, quantity)
                else:
                    order = self.order_manager.place_limit_order(symbol, side, quantity, price)
                
                progress.update(task, completed=True)
            
            # Display result
            self.display_order_result(order)
            
            # Log success
            logger.info(f"Order placed successfully: {order.get('orderId')}")
            
            return order
            
        except ValidationError as e:
            console.print(f"[red]❌ Validation Error: {e}[/red]")
            logger.error(f"Validation error: {e}")
        except APIError as e:
            console.print(f"[red]❌ API Error: {e}[/red]")
            logger.error(f"API error: {e}")
        except NetworkError as e:
            console.print(f"[red]❌ Network Error: {e}[/red]")
            logger.error(f"Network error: {e}")
        except Exception as e:
            console.print(f"[red]❌ Unexpected Error: {e}[/red]")
            logger.error(f"Unexpected error: {e}")
        
        return None

@click.group()
def cli():
    """Professional Trading Bot for Binance Futures Testnet"""
    pass

@cli.command()
@click.option('--symbol', prompt='Symbol', default=lambda: os.getenv('DEFAULT_SYMBOL', 'BTCUSDT'))
@click.option('--side', type=click.Choice(['BUY', 'SELL'], case_sensitive=False), prompt='Side')
@click.option('--order-type', type=click.Choice(['MARKET', 'LIMIT'], case_sensitive=False), prompt='Order type')
@click.option('--quantity', type=float, prompt='Quantity')
@click.option('--price', type=float, help='Price for LIMIT orders')
def order(symbol, side, order_type, quantity, price):
    """Place a trading order"""
    bot = ProfessionalTradingBot()
    bot.display_banner()
    
    if not bot.initialize():
        return
    
    # Validate price for limit orders
    if order_type.upper() == 'LIMIT' and not price:
        price = click.prompt('Price (USDT)', type=float)
    
    bot.place_order(symbol.upper(), side.upper(), order_type.upper(), quantity, price)

@cli.command()
def balance():
    """Check account balance"""
    bot = ProfessionalTradingBot()
    bot.display_banner()
    
    if not bot.initialize():
        return
    
    bot.check_balance()

@cli.command()
def interactive():
    """Interactive mode with guided prompts"""
    bot = ProfessionalTradingBot()
    bot.display_banner()
    
    if not bot.initialize():
        return
    
    console.print("[cyan]🎮 Interactive Trading Mode[/cyan]\n")
    
    # Show balance first
    bot.check_balance()
    
    # Guided order placement
    symbol = Prompt.ask("Symbol", default="BTCUSDT")
    side = Prompt.ask("Side", choices=["BUY", "SELL"], default="BUY")
    order_type = Prompt.ask("Order type", choices=["MARKET", "LIMIT"], default="MARKET")
    quantity = float(Prompt.ask("Quantity", default="0.001"))
    
    price = None
    if order_type == "LIMIT":
        price = float(Prompt.ask("Price (USDT)"))
    
    bot.place_order(symbol.upper(), side.upper(), order_type.upper(), quantity, price)

if __name__ == '__main__':
    cli()
