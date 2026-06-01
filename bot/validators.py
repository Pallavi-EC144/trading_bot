import re
from typing import Tuple

class OrderValidator:
    """Validate order parameters"""
    
    VALID_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOGEUSDT']
    VALID_SIDES = ['BUY', 'SELL']
    VALID_ORDER_TYPES = ['MARKET', 'LIMIT']
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> Tuple[bool, str]:
        """Validate trading symbol"""
        symbol = symbol.upper()
        if symbol not in cls.VALID_SYMBOLS:
            return False, f"Invalid symbol. Supported: {', '.join(cls.VALID_SYMBOLS)}"
        return True, symbol
    
    @classmethod
    def validate_side(cls, side: str) -> Tuple[bool, str]:
        """Validate order side"""
        side = side.upper()
        if side not in cls.VALID_SIDES:
            return False, f"Invalid side. Must be {', '.join(cls.VALID_SIDES)}"
        return True, side
    
    @classmethod
    def validate_order_type(cls, order_type: str) -> Tuple[bool, str]:
        """Validate order type"""
        order_type = order_type.upper()
        if order_type not in cls.VALID_ORDER_TYPES:
            return False, f"Invalid order type. Must be {', '.join(cls.VALID_ORDER_TYPES)}"
        return True, order_type
    
    @classmethod
    def validate_quantity(cls, quantity: float, symbol: str) -> Tuple[bool, str]:
        """Validate order quantity"""
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        
        # Basic lot size validation (simplified)
        if symbol == 'BTCUSDT' and quantity < 0.001:
            return False, "Minimum quantity for BTCUSDT is 0.001"
        elif symbol == 'ETHUSDT' and quantity < 0.01:
            return False, "Minimum quantity for ETHUSDT is 0.01"
        elif quantity < 1:
            return False, f"Minimum quantity for {symbol} is 1"
        
        return True, ""
    
    @classmethod
    def validate_price(cls, price: float) -> Tuple[bool, str]:
        """Validate limit order price"""
        if price <= 0:
            return False, "Price must be greater than 0"
        return True, ""
