"""Custom exceptions for the trading bot"""

class TradingBotError(Exception):
    """Base exception for trading bot"""
    pass

class ValidationError(TradingBotError):
    """Raised when input validation fails"""
    pass

class APIError(TradingBotError):
    """Raised when Binance API returns an error"""
    pass

class NetworkError(TradingBotError):
    """Raised when network connection fails"""
    pass

class InsufficientBalanceError(TradingBotError):
    """Raised when account has insufficient balance"""
    pass
