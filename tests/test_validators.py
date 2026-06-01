import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.validators import OrderValidator
import pytest

def test_valid_symbol():
    is_valid, result = OrderValidator.validate_symbol("BTCUSDT")
    assert is_valid == True
    assert result == "BTCUSDT"

def test_invalid_symbol():
    is_valid, result = OrderValidator.validate_symbol("INVALID")
    assert is_valid == False

def test_valid_side():
    is_valid, result = OrderValidator.validate_side("BUY")
    assert is_valid == True

def test_invalid_side():
    is_valid, result = OrderValidator.validate_side("INVALID")
    assert is_valid == False

def test_valid_quantity_btc():
    is_valid, msg = OrderValidator.validate_quantity(0.001, "BTCUSDT")
    assert is_valid == True

def test_invalid_quantity_too_small():
    is_valid, msg = OrderValidator.validate_quantity(0.0001, "BTCUSDT")
    assert is_valid == False

def test_valid_price():
    is_valid, msg = OrderValidator.validate_price(100)
    assert is_valid == True

def test_invalid_price():
    is_valid, msg = OrderValidator.validate_price(-10)
    assert is_valid == False

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
