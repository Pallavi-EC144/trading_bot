#!/usr/bin/env python3
"""
Trading Bot Web UI - Binance Futures Testnet
Deployable on Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
import sys
from pathlib import Path

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent))

from bot.logging_config import setup_logging
from bot.client import BinanceFuturesClient
from bot.orders import OrderManager
from bot.validators import OrderValidator

# Page configuration
st.set_page_config(
    page_title="Primetrade Trading Bot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #f0f2f6;
        color: #1e1e2f;
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
    .order-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin: 0.5rem 0;
        border-left: 4px solid #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'order_history' not in st.session_state:
    st.session_state.order_history = []
if 'client' not in st.session_state:
    st.session_state.client = None
if 'order_manager' not in st.session_state:
    st.session_state.order_manager = None
if 'connected' not in st.session_state:
    st.session_state.connected = False

class StreamlitTradingBot:
    """Wrapper for Streamlit UI"""
    
    def __init__(self):
        self.logger = setup_logging()
        
    def initialize_client(self, api_key: str, api_secret: str) -> bool:
        """Initialize the Binance client"""
        try:
            st.session_state.client = BinanceFuturesClient(api_key, api_secret)
            st.session_state.order_manager = OrderManager(st.session_state.client)
            
            # Test connection
            account = st.session_state.client.get_account_info()
            st.session_state.connected = True
            self.logger.info("Successfully connected to Binance Futures Testnet")
            return True
        except Exception as e:
            st.session_state.connected = False
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: float = None) -> dict:
        """Place an order and return result"""
        try:
            if order_type.upper() == 'MARKET':
                order = st.session_state.order_manager.place_market_order(
                    symbol, side, quantity
                )
            else:  # LIMIT
                if not price:
                    raise ValueError("Price required for LIMIT orders")
                order = st.session_state.order_manager.place_limit_order(
                    symbol, side, quantity, price
                )
            
            # Add to history
            st.session_state.order_history.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity,
                'price': price,
                'order_id': order.get('orderId'),
                'status': order.get('status'),
                'executed_qty': order.get('executedQty'),
                'avg_price': order.get('avgPrice')
            })
            
            return {'success': True, 'order': order}
            
        except Exception as e:
            self.logger.error(f"Order failed: {e}")
            return {'success': False, 'error': str(e)}

def main():
    """Main Streamlit application"""
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🚀 Primetrade.ai Trading Bot")
        st.caption("Binance Futures Testnet | Professional Trading Interface")
    
    st.markdown("---")
    
    # Sidebar - Connection Settings
    with st.sidebar:
        st.header("🔐 Connection Settings")
        
        # API Key inputs
        api_key = st.text_input("API Key", type="password", 
                                help="Enter your Binance Testnet API Key")
        api_secret = st.text_input("API Secret", type="password",
                                   help="Enter your Binance Testnet API Secret")
        
        # Or use environment variables
        use_env = st.checkbox("Use environment variables (.env file)")
        if use_env:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('BINANCE_API_KEY', '')
            api_secret = os.getenv('BINANCE_API_SECRET', '')
            st.info("Using credentials from .env file")
        
        # Connect button
        if st.button("🔌 Connect to Testnet", type="primary"):
            if api_key and api_secret:
                bot = StreamlitTradingBot()
                if bot.initialize_client(api_key, api_secret):
                    st.success("✅ Connected successfully!")
                    st.session_state.bot_instance = bot
                    st.rerun()
                else:
                    st.error("❌ Connection failed. Check credentials and network.")
            else:
                st.warning("Please enter API credentials")
        
        # Connection status
        if st.session_state.connected:
            st.success("🟢 Connected to Binance Futures Testnet")
        else:
            st.error("🔴 Not connected")
        
        st.markdown("---")
        
        # Account Info
        if st.session_state.connected and st.session_state.client:
            st.header("💰 Account Info")
            try:
                account = st.session_state.client.get_account_info()
                st.metric("Account Type", "Futures Testnet")
                
                # Show balances
                if 'assets' in account:
                    st.subheader("Balances")
                    for asset in account['assets'][:5]:  # Show top 5
                        if float(asset['walletBalance']) > 0:
                            st.metric(
                                asset['asset'], 
                                f"{float(asset['walletBalance']):.2f}"
                            )
            except Exception as e:
                st.error(f"Could not fetch account info: {e}")
        
        st.markdown("---")
        st.caption("⚠️ **Disclaimer**: For testing purposes only")
    
    # Main content area
    if not st.session_state.connected:
        st.info("👈 Please connect your Binance Futures Testnet account using the sidebar")
        
        # Show setup instructions
        with st.expander("📖 How to get started"):
            st.markdown("""
            1. **Create a Binance Testnet account** at [testnet.binancefuture.com](https://testnet.binancefuture.com)
            2. **Generate API credentials** (API Key and Secret)
            3. **Fund your account** using the faucet (get free test USDT)
            4. **Enter credentials** in the sidebar and click Connect
            5. **Place orders** using the form below
            """)
        return
    
    # Trading Interface
    st.header("📊 Place Order")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Order Parameters")
        
        # Order form
        with st.form("order_form"):
            # Symbol selection
            symbol = st.selectbox(
                "Trading Pair",
                options=['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOGEUSDT', 'SOLUSDT', 'XRPUSDT'],
                help="Select the cryptocurrency pair to trade"
            )
            
            # Side selection with visual indicators
            col_side1, col_side2 = st.columns(2)
            with col_side1:
                side = st.radio(
                    "Side",
                    options=['BUY', 'SELL'],
                    horizontal=True,
                    help="BUY (Long) or SELL (Short)"
                )
            
            # Order type
            order_type = st.radio(
                "Order Type",
                options=['MARKET', 'LIMIT'],
                horizontal=True,
                help="MARKET (executes immediately) or LIMIT (executes at specific price)"
            )
            
            # Quantity
            quantity = st.number_input(
                "Quantity",
                min_value=0.001 if symbol == 'BTCUSDT' else 0.01,
                step=0.001 if symbol == 'BTCUSDT' else 0.01,
                format="%.3f",
                help=f"Minimum: {0.001 if symbol == 'BTCUSDT' else 0.01}"
            )
            
            # Price (only for LIMIT orders)
            price = None
            if order_type == 'LIMIT':
                price = st.number_input(
                    "Price (USDT)",
                    min_value=0.01,
                    step=1.0,
                    format="%.2f",
                    help="Limit price for the order"
                )
                
                # Get current market price
                if st.button("📈 Get Current Price", type="secondary"):
                    try:
                        current_price = st.session_state.client.get_symbol_price(symbol)
                        st.info(f"Current {symbol} price: ${current_price:,.2f}")
                        price = current_price
                    except:
                        st.error("Could not fetch current price")
            
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
                    # Place the order
                    bot = st.session_state.bot_instance
                    result = bot.place_order(symbol, side, order_type, quantity, price)
                    
                    if result['success']:
                        order = result['order']
                        st.markdown('<div class="success-message">', unsafe_allow_html=True)
                        st.success("✅ Order placed successfully!")
                        st.json({
                            "Order ID": order.get('orderId'),
                            "Status": order.get('status'),
                            "Executed Quantity": order.get('executedQty'),
                            "Average Price": order.get('avgPrice', 'N/A')
                        })
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.markdown('<div class="error-message">', unsafe_allow_html=True)
                        st.error(f"❌ Order failed: {result['error']}")
                        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("📈 Market Information")
        
        # Live price ticker
        if st.session_state.client:
            try:
                # Get prices for major pairs
                symbols_to_show = ['BTCUSDT', 'ETHUSDT']
                for sym in symbols_to_show:
                    price = st.session_state.client.get_symbol_price(sym)
                    change_pct = 0  # Would need historical data for real change
                    
                    col_price, col_change = st.columns(2)
                    with col_price:
                        st.metric(
                            sym,
                            f"${price:,.2f}",
                            delta=None,
                            help=f"Current {sym} price"
                        )
                    
                # Order book depth (simplified)
                st.subheader("Quick Tips")
                st.info("""
                **Order Types:**
                - **MARKET**: Executes immediately at current market price
                - **LIMIT**: Executes only at your specified price
                
                **Minimum Quantities:**
                - BTCUSDT: 0.001
                - ETHUSDT: 0.01
                - Other pairs: 1
                """)
                
            except Exception as e:
                st.error(f"Could not fetch market data: {e}")
    
    # Order History
    st.markdown("---")
    st.header("📜 Order History")
    
    if st.session_state.order_history:
        # Convert to DataFrame for display
        df = pd.DataFrame(st.session_state.order_history)
        df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Color coding for BUY/SELL
        def highlight_side(val):
            if val == 'BUY':
                return 'background-color: #d4edda'
            elif val == 'SELL':
                return 'background-color: #f8d7da'
            return ''
        
        # Display dataframe with styling
        st.dataframe(
            df[['timestamp', 'symbol', 'side', 'type', 'quantity', 'price', 'status', 'executed_qty']],
            use_container_width=True,
            hide_index=True
        )
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            total_orders = len(st.session_state.order_history)
            st.metric("Total Orders", total_orders)
        with col2:
            buy_orders = len([o for o in st.session_state.order_history if o['side'] == 'BUY'])
            st.metric("BUY Orders", buy_orders)
        with col3:
            sell_orders = len([o for o in st.session_state.order_history if o['side'] == 'SELL'])
            st.metric("SELL Orders", sell_orders)
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.order_history = []
            st.rerun()
    else:
        st.info("No orders placed yet. Use the form to place your first order!")
    
    # Real-time log viewer
    with st.expander("📋 Live Logs"):
        log_file = st.selectbox(
            "Select log file",
            options=['latest'] + [f for f in os.listdir('logs') if f.endswith('.log')][:5] 
            if os.path.exists('logs') else []
        )
        
        if log_file and log_file != 'latest' and os.path.exists(f'logs/{log_file}'):
            with open(f'logs/{log_file}', 'r') as f:
                log_content = f.read()[-5000:]  # Last 5000 characters
                st.code(log_content, language='log')
        elif os.path.exists('logs'):
            # Show most recent log
            log_files = [f for f in os.listdir('logs') if f.endswith('.log')]
            if log_files:
                latest_log = max(log_files, key=lambda x: os.path.getctime(f'logs/{x}'))
                with open(f'logs/{latest_log}', 'r') as f:
                    log_content = f.read()[-5000:]
                    st.code(log_content, language='log')

if __name__ == "__main__":
    main()
