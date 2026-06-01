import requests
import hashlib
import hmac
import time
from typing import Dict, Optional
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)

class BinanceFuturesClient:
    """Binance Futures Testnet API Client"""
    
    BASE_URL = "https://testnet.binancefuture.com"
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        })
        
    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, signed: bool = False) -> Dict:
        """Make API request to Binance"""
        url = f"{self.BASE_URL}{endpoint}"
        
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['recvWindow'] = 5000
            params['signature'] = self._generate_signature(params)
        
        try:
            logger.debug(f"API Request: {method} {endpoint} | Params: {params}")
            
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'POST':
                response = self.session.post(url, params=params if signed else None, json=params if not signed else None)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            logger.debug(f"API Response: {response.status_code} | {response.text[:200]}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request failed: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response body: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    def get_account_info(self) -> Dict:
        """Get futures account information"""
        return self._request('GET', '/fapi/v2/account', signed=True)
    
    def get_symbol_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        response = self._request('GET', '/fapi/v1/ticker/price', params={'symbol': symbol})
        return float(response['price'])
    
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None) -> Dict:
        """Place an order on Binance Futures"""
        
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity
        }
        
        if order_type == 'LIMIT':
            if price is None:
                raise ValueError("Price is required for LIMIT orders")
            params['price'] = price
            params['timeInForce'] = 'GTC'
        
        logger.info(f"Placing {order_type} order: {side} {quantity} {symbol} @ {price if price else 'MARKET'}")
        
        response = self._request('POST', '/fapi/v1/order', params=params, signed=True)
        return response
