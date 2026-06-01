from typing import Dict, Optional
import logging
from .client import BinanceFuturesClient
from .validators import OrderValidator

logger = logging.getLogger(__name__)

class OrderManager:
    """Handle order placement and management"""
    
    def __init__(self, client: BinanceFuturesClient):
        self.client = client
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """Place a market order"""
        # Validate parameters
        is_valid, msg = OrderValidator.validate_symbol(symbol)
        if not is_valid:
            raise ValueError(msg)
        symbol = msg
        
        is_valid, msg = OrderValidator.validate_side(side)
        if not is_valid:
            raise ValueError(msg)
        side = msg
        
        is_valid, msg = OrderValidator.validate_quantity(quantity, symbol)
        if not is_valid:
            raise ValueError(msg)
        
        # Place market order
        order = self.client.place_order(symbol, side, 'MARKET', quantity)
        return order
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict:
        """Place a limit order"""
        # Validate parameters
        is_valid, msg = OrderValidator.validate_symbol(symbol)
        if not is_valid:
            raise ValueError(msg)
        symbol = msg
        
        is_valid, msg = OrderValidator.validate_side(side)
        if not is_valid:
            raise ValueError(msg)
        side = msg
        
        is_valid, msg = OrderValidator.validate_quantity(quantity, symbol)
        if not is_valid:
            raise ValueError(msg)
        
        is_valid, msg = OrderValidator.validate_price(price)
        if not is_valid:
            raise ValueError(msg)
        
        # Place limit order
        order = self.client.place_order(symbol, side, 'LIMIT', quantity, price)
        return order
    
    def format_order_response(self, order: Dict) -> str:
        """Format order response for display"""
        output = [
            "=" * 60,
            f"Order ID: {order.get('orderId')}",
            f"Symbol: {order.get('symbol')}",
            f"Side: {order.get('side')}",
            f"Type: {order.get('type')}",
            f"Quantity: {order.get('origQty')}",
        ]
        
        if order.get('price') and float(order.get('price')) > 0:
            output.append(f"Price: {order.get('price')}")
        
        output.append(f"Status: {order.get('status')}")
        
        if order.get('executedQty') and float(order.get('executedQty')) > 0:
            output.append(f"Executed Quantity: {order.get('executedQty')}")
        
        if order.get('avgPrice') and float(order.get('avgPrice')) > 0:
            output.append(f"Average Price: {order.get('avgPrice')}")
        
        output.append("=" * 60)
        return "\n".join(output)
