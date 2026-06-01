#!/usr/bin/env python3
"""
Complete Standalone Trading Bot - Binance Futures Testnet
No external dependencies except streamlit and requests
"""

import streamlit as st
import requests
import hashlib
import hmac
import time
import json
from datetime import datetime
from urllib.parse import urlencode

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
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'order_history' not in st.session_state:
    st.session_state.order_history = []
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'client' not in st.session_state:
    st.session_state.client = None

class BinanceFuturesClient:
    """Complete Binance Futures Testnet Client"""
    
    BASE_URL = "https://testnet.binancefuture.com"
    
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        })
    
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
        """Make API request to Binance"""
        url = f"{self.BASE_URL}{endpoint}"
        
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['recvWindow'] = 5000
            params['signature'] = self._generate_signature(params)
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'POST':
                response = self.session.post(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response:
                error_msg = e.response.json().get('msg', str(e))
                raise Exception(f"API Error: {error_msg}")
            raise Exception(f"Network Error: {str(e)}")
    
    def get_account_info(self):
        """Get futures account information"""
        return self._request('GET', '/fapi/v2/account', signed=True)
    
    def get_symbol_price(self, symbol):
        """Get current price for symbol"""
        response = self._request('GET', '/fapi/v1/ticker/price', params={'symbol': symbol})
        return float(response['price'])
    
    def place_order(self, symbol, side, order_type, quantity, price=None):
        """Place an order on Binance Futures"""
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': float(quantity)
        }
        
        if order_type == 'LIMIT':
            if price is None:
                raise ValueError("Price is required for LIMIT orders")
            params['price'] = float(price)
            params['timeInForce'] = 'GTC'
        
        response = self._request('POST', '/fapi/v1/order', params=params, signed=True)
        return response

def main():
    # Header
    st.title("🚀 Primetrade.ai Trading Bot")
    st.caption("Binance Futures Testnet - Professional Trading Interface")
    st.markdown("---")
    
    # Sidebar for connection
    with st.sidebar:
        st.header("🔐 Connection Settings")
        
        # API Key inputs
        api_key = st.text_input("API Key", type="password", 
                               help="Enter your Binance Testnet API Key")
        api_secret = st.text_input("API Secret", type="password",
                                  help="Enter your Binance Testnet API Secret")
        
        # Connect button
        if st.button("🔌 Connect to Testnet", type="primary"):
            if api_key and api_secret:
                try:
                    with st.spinner("Connecting to Binance..."):
                        st.session_state.client = BinanceFuturesClient(api_key, api_secret)
                        account = st.session_state.client.get_account_info()
                        st.session_state.connected = True
                        st.success("✅ Connected successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
                    st.session_state.connected = False
            else:
                st.warning("⚠️ Please enter API credentials")
        
        # Connection status
        if st.session_state.connected:
            st.success("🟢 Connected to Binance Futures Testnet")
            
            # Show account info
            if st.session_state.client:
                try:
                    st.markdown("---")
                    st.header("💰 Account Balance")
                    account = st.session_state.client.get_account_info()
                    
                    if 'assets' in account:
                        for asset in account['assets']:
                            balance = float(asset.get('walletBalance', 0))
                            if balance > 0:
                                st.metric(
                                    asset['asset'], 
                                    f"{balance:.2f}",
                                    delta=None
                                )
                except Exception as e:
                    st.error(f"Could not fetch balance: {str(e)}")
        else:
            st.info("💡 Not connected. Enter your API credentials and click Connect.")
    
    # Main trading area
    if not st.session_state.connected:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.subheader("📖 How to Get Started")
            st.markdown("""
            1. **Create a Binance Testnet account** at [testnet.binancefuture.com](https://testnet.binancefuture.com)
            2. **Generate API credentials** (API Key and Secret)
            3. **Fund your account** using the faucet (get free test USDT)
            4. **Enter credentials** in the sidebar and click Connect
            5. **Place your first order** using the form below
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Trading Interface
    st.header("📊 Place Order")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("order_form"):
            st.subheader("Order Parameters")
            
            # Symbol selection
            symbol = st.selectbox(
                "💰 Trading Pair",
                options=['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOGEUSDT', 'SOLUSDT', 'XRPUSDT'],
                help="Select the cryptocurrency pair to trade"
            )
            
            # Side selection
            side = st.radio(
                "📈 Side",
                options=['BUY', 'SELL'],
                horizontal=True,
                help="BUY (Long) or SELL (Short)"
            )
            
            # Order type
            order_type = st.radio(
                "⚡ Order Type",
                options=['MARKET', 'LIMIT'],
                horizontal=True,
                help="MARKET (executes immediately) or LIMIT (executes at specific price)"
            )
            
            # Quantity
            min_qty = 0.001 if 'BTC' in symbol else 0.01
            quantity = st.number_input(
                "📦 Quantity",
                min_value=min_qty,
                value=min_qty,
                step=min_qty,
                format="%.3f",
                help=f"Minimum quantity: {min_qty}"
            )
            
            # Price (only for LIMIT orders)
            price = None
            if order_type == 'LIMIT':
                price = st.number_input(
                    "💵 Price (USDT)",
                    min_value=0.01,
                    value=100.0,
                    step=1.0,
                    format="%.2f",
                    help="Limit price for the order"
                )
                
                # Get current market price button
                if st.button("📈 Get Current Market Price"):
                    try:
                        current_price = st.session_state.client.get_symbol_price(symbol)
                        st.info(f"💰 Current {symbol} price: ${current_price:,.2f}")
                        price = current_price
                    except Exception as e:
                        st.error(f"Could not fetch price: {str(e)}")
            
            # Submit button
            submitted = st.form_submit_button(
                f"🚀 Place {order_type} {side} Order",
                type="primary",
                use_container_width=True
            )
            
            if submitted:
                if quantity <= 0:
                    st.error("❌ Quantity must be greater than 0")
                elif order_type == 'LIMIT' and (not price or price <= 0):
                    st.error("❌ Valid price required for LIMIT orders")
                else:
                    try:
                        # Place the order
                        order = st.session_state.client.place_order(
                            symbol, side, order_type, quantity, price
                        )
                        
                        # Add to history
                        st.session_state.order_history.append({
                            'Time': datetime.now().strftime('%H:%M:%S'),
                            'Date': datetime.now().strftime('%Y-%m-%d'),
                            'Symbol': symbol,
                            'Side': side,
                            'Type': order_type,
                            'Quantity': quantity,
                            'Price': price if price else 'MARKET',
                            'Order ID': order.get('orderId'),
                            'Status': order.get('status'),
                            'Executed': order.get('executedQty', '0'),
                            'Avg Price': order.get('avgPrice', 'N/A')
                        })
                        
                        # Show success message
                        st.markdown('<div class="success-message">', unsafe_allow_html=True)
                        st.success("✅ ORDER PLACED SUCCESSFULLY!")
                        st.json({
                            "Order ID": order.get('orderId'),
                            "Symbol": order.get('symbol'),
                            "Side": order.get('side'),
                            "Type": order.get('type'),
                            "Quantity": order.get('origQty'),
                            "Price": order.get('price', 'MARKET'),
                            "Status": order.get('status'),
                            "Executed Quantity": order.get('executedQty', '0'),
                            "Average Price": order.get('avgPrice', 'N/A')
                        })
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.balloons()
                        
                    except Exception as e:
                        st.markdown('<div class="error-message">', unsafe_allow_html=True)
                        st.error(f"❌ Order failed: {str(e)}")
                        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("📈 Market Information")
        
        # Live price ticker
        try:
            st.markdown("### Current Prices")
            for sym in ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']:
                price = st.session_state.client.get_symbol_price(sym)
                col_price, col_change = st.columns([2, 1])
                with col_price:
                    st.metric(sym, f"${price:,.2f}")
        except Exception as e:
            st.info("Click 'Get Current Market Price' to see prices")
        
        st.markdown("---")
        st.subheader("📋 Quick Reference")
        st.info("""
        **Minimum Order Quantities:**
        - **BTCUSDT**: 0.001 BTC
        - **ETHUSDT**: 0.01 ETH  
        - **BNBUSDT**: 0.01 BNB
        - **Other pairs**: 1 unit
        
        **Order Types Explained:**
        - **MARKET**: Buys/Sells immediately at current market price
        - **LIMIT**: Sets a specific price - order executes when market hits that price
        
        **Tips:**
        - Always verify your balance before trading
        - Start with small quantities for testing
        - Check order status in history below
        """)
    
    # Order History
    st.markdown("---")
    st.header("📜 Order History")
    
    if st.session_state.order_history:
        # Display as table
        st.dataframe(
            st.session_state.order_history[::-1],  # Show newest first
            use_container_width=True,
            hide_index=True,
            column_config={
                "Order ID": st.column_config.TextColumn("Order ID", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small"),
            }
        )
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_orders = len(st.session_state.order_history)
            st.metric("Total Orders", total_orders)
        with col2:
            buy_orders = len([o for o in st.session_state.order_history if o['Side'] == 'BUY'])
            st.metric("BUY Orders", buy_orders)
        with col3:
            sell_orders = len([o for o in st.session_state.order_history if o['Side'] == 'SELL'])
            st.metric("SELL Orders", sell_orders)
        with col4:
            market_orders = len([o for o in st.session_state.order_history if o['Type'] == 'MARKET'])
            st.metric("Market Orders", market_orders)
        
        # Clear history button
        if st.button("🗑️ Clear Order History", use_container_width=True):
            st.session_state.order_history = []
            st.rerun()
    else:
        st.info("📭 No orders placed yet. Use the form to place your first order!")

if __name__ == "__main__":
    main()
