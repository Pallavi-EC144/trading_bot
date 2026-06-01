#!/usr/bin/env python3
"""
Trading Bot Web UI - Binance Futures Testnet
Simplified version that works on Streamlit Cloud
"""

import streamlit as st
from datetime import datetime
import os
import sys
import json
import requests
import hashlib
import hmac
import time
from urllib.parse import urlencode
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="Primetrade Trading Bot",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'order_history' not in st.session_state:
    st.session_state.order_history = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'api_secret' not in st.session_state:
    st.session_state.api_secret = None
if 'connected' not in st.session_state:
    st.session_state.connected = False

class BinanceFuturesClient:
    """Simplified Binance Futures Testnet Client"""
    
    BASE_URL = "https://testnet.binancefuture.com"
    
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        
    def _generate_signature(self, params):
        """Generate HMAC SHA256 signature"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method, endpoint, params=None, signed=False):
        """Make API request"""
        url = f"{self.BASE_URL}{endpoint}"
        
        if params is None:
            params = {}
        
        headers = {'X-MBX-APIKEY': self.api_key}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['recvWindow'] = 5000
            params['signature'] = self._generate_signature(params)
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers)
            elif method == 'POST':
                response = requests.post(url, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            raise
    
    def get_account_info(self):
        """Get account information"""
        return self._request('GET', '/fapi/v2/account', signed=True)
    
    def get_symbol_price(self, symbol):
        """Get current price"""
        response = self._request('GET', '/fapi/v1/ticker/price', params={'symbol': symbol})
        return float(response['price'])
    
    def place_order(self, symbol, side, order_type, quantity, price=None):
        """Place an order"""
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity
        }
        
        if order_type == 'LIMIT':
            if price is None:
                raise ValueError("Price required for LIMIT orders")
            params['price'] = price
            params['timeInForce'] = 'GTC'
        
        response = self._request('POST', '/fapi/v1/order', params=params, signed=True)
        return response

def main():
    st.title("🚀 Primetrade.ai Trading Bot")
    st.caption("Binance Futures Testnet")
    st.markdown("---")
    
    # Sidebar - Connection
    with st.sidebar:
        st.header("🔐 Connection")
        
        api_key = st.text_input("API Key", type="password")
        api_secret = st.text_input("API Secret", type="password")
        
        use_env = st.checkbox("Use .env file (for local)")
        if use_env:
            load_dotenv()
            api_key = os.getenv('BINANCE_API_KEY', '')
            api_secret = os.getenv('BINANCE_API_SECRET', '')
            if api_key:
                st.success("Loaded from .env")
        
        if st.button("Connect", type="primary"):
            if api_key and api_secret:
                try:
                    st.session_state.client = BinanceFuturesClient(api_key, api_secret)
                    account = st.session_state.client.get_account_info()
                    st.session_state.connected = True
                    st.session_state.api_key = api_key
                    st.session_state.api_secret = api_secret
                    st.success("✅ Connected!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Connection failed: {e}")
            else:
                st.warning("Enter API credentials")
        
        if st.session_state.connected:
            st.success("🟢 Connected")
            
            # Show balances
            try:
                if hasattr(st.session_state, 'client'):
                    account = st.session_state.client.get_account_info()
                    st.subheader("Balances")
                    for asset in account.get('assets', [])[:3]:
                        balance = float(asset.get('walletBalance', 0))
                        if balance > 0:
                            st.metric(asset['asset'], f"{balance:.2f}")
            except:
                pass
    
    # Main trading interface
    if not st.session_state.connected:
        st.info("👈 Connect your Binance Futures Testnet account using the sidebar")
        st.markdown("""
        ### How to get credentials:
        1. Go to [Binance Futures Testnet](https://testnet.binancefuture.com/)
        2. Create an account
        3. Generate API credentials
        4. Fund your account with test USDT
        5. Enter credentials in the sidebar
        """)
        return
    
    # Trading form
    st.header("Place Order")
    
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.selectbox(
            "Symbol",
            ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOGEUSDT', 'SOLUSDT']
        )
        
        side = st.radio("Side", ['BUY', 'SELL'], horizontal=True)
        
        order_type = st.radio("Order Type", ['MARKET', 'LIMIT'], horizontal=True)
        
        quantity = st.number_input(
            "Quantity",
            min_value=0.001 if 'BTC' in symbol else 0.01,
            step=0.001,
            format="%.3f"
        )
        
        price = None
        if order_type == 'LIMIT':
            price = st.number_input("Price (USDT)", min_value=0.01, step=1.0, format="%.2f")
            
            # Get current price button
            if st.button("Get Current Price"):
                try:
                    current_price = st.session_state.client.get_symbol_price(symbol)
                    st.info(f"Current price: ${current_price:,.2f}")
                except:
                    st.error("Could not fetch price")
        
        if st.button(f"Place {order_type} {side} Order", type="primary"):
            try:
                client = st.session_state.client
                
                if order_type == 'MARKET':
                    order = client.place_order(symbol, side, 'MARKET', quantity)
                else:
                    if not price:
                        st.error("Price required for LIMIT orders")
                        st.stop()
                    order = client.place_order(symbol, side, 'LIMIT', quantity, price)
                
                # Add to history
                st.session_state.order_history.append({
                    'Time': datetime.now().strftime('%H:%M:%S'),
                    'Symbol': symbol,
                    'Side': side,
                    'Type': order_type,
                    'Qty': quantity,
                    'Price': price if price else 'MARKET',
                    'Status': order.get('status'),
                    'Order ID': order.get('orderId')
                })
                
                st.markdown('<div class="success-message">', unsafe_allow_html=True)
                st.success("✅ Order placed successfully!")
                st.json({
                    "Order ID": order.get('orderId'),
                    "Status": order.get('status'),
                    "Symbol": order.get('symbol'),
                    "Side": order.get('side'),
                    "Quantity": order.get('origQty'),
                    "Executed": order.get('executedQty'),
                    "Avg Price": order.get('avgPrice', 'N/A')
                })
                st.markdown('</div>', unsafe_allow_html=True)
                st.balloons()
                
            except Exception as e:
                st.markdown('<div class="error-message">', unsafe_allow_html=True)
                st.error(f"❌ Order failed: {str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("Market Info")
        
        # Show current prices
        try:
            client = st.session_state.client
            for sym in ['BTCUSDT', 'ETHUSDT']:
                price = client.get_symbol_price(sym)
                st.metric(sym, f"${price:,.2f}")
        except:
            st.info("Click 'Get Current Price' to see market data")
        
        st.markdown("---")
        st.subheader("Quick Tips")
        st.info("""
        **Minimum Quantities:**
        - BTCUSDT: 0.001
        - ETHUSDT: 0.01
        - Other pairs: 1
        
        **Order Types:**
        - MARKET: Executes immediately
        - LIMIT: Executes at specific price
        """)
    
    # Order History
    st.markdown("---")
    st.header("Order History")
    
    if st.session_state.order_history:
        st.dataframe(
            st.session_state.order_history,
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("Clear History"):
            st.session_state.order_history = []
            st.rerun()
    else:
        st.info("No orders placed yet")

if __name__ == "__main__":
    main()
