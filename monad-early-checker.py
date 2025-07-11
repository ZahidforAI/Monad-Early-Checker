import streamlit as st
import requests
from datetime import datetime, timezone
from web3 import Web3

# === CONFIG ===
API_KEY = "8f9d3e27-a516-4c08-b235-7d94f02ca91b"
RPC_URL = "https://rpc.ankr.com/monad_testnet"
SCAN_API = "https://api.socialscan.io/monad-testnet/v1/developer/api"

TIERS = [
    (5_000_000, "🟣 Super Early"),
    (10_000_000, "🔵 Early"),
    (20_000_000, "🟡 Late"),
    (float("inf"), "🔴 Recently Joined")
]

# === Get latest block ===
def get_latest_block():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        return None
    return w3.eth.block_number

# === Get first TX ===
def get_first_tx(wallet):
    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet,
        "startblock": 0,
        "endblock": 999999999,
        "page": 1,
        "offset": 1,
        "sort": "asc",
        "apikey": API_KEY
    }
    try:
        res = requests.get(SCAN_API, params=params)
        res.raise_for_status()
        data = res.json()
        if data["status"] != "1" or not data["result"]:
            return None
        return data["result"][0]
    except:
        return None

# === Score and Tier ===
def calculate_score(first_block, latest_block):
    return round((1 - (int(first_block) / latest_block)) * 100, 2)

def get_tier(block_num):
    for threshold, label in TIERS:
        if block_num < threshold:
            return label
    return "🔴 Unknown"

# === Streamlit UI ===
st.set_page_config(page_title="Monad Early Checker", page_icon="🚀")

st.markdown("""
<style>
/* Background & Font */
html, body, .stApp {
    height: 100%;
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 50%, #6D28D9 100%);
    color: white;
    overflow-y: auto !important;
}

/* Ensure inner content scrolls */
main > div {
    overflow-y: auto;
    max-height: 100vh;
}

/* Input styling */
input, .stTextInput>div>div>input {
    background-color: white !important;
    color: black !important;
    border-radius: 10px;
}

/* Button styling */
.stButton>button {
    background-color: #7C3AED;
    color: white;
    border-radius: 10px;
    font-weight: bold;
    padding: 10px 20px;
}

/* Result font */
.result-highlight {
    font-size: 1.8rem;
    font-weight: bold;
    color: #fff;
    margin-top: 20px;
    text-align: center;
}

/* Responsive */
@media screen and (max-width: 600px) {
    .result-highlight {
        font-size: 1.5rem;
    }
}
</style>
""", unsafe_allow_html=True)


# === CSS Styling ===
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 50%, #6D28D9 100%) !important;
        color: white;
        text-align: center;
    }
    .block-container {
        max-width: 600px;
        margin: 0.5rem;
        padding: 2rem;
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        color: black;
    }
    .result-box {
        font-size: 2.5rem;
        font-weight: 800;
        color: #7C3AED;
        margin-top: 20px;
    }
    .info-text {
        font-size: 1.1rem;
        font-weight: 500;
        color: #333;
    }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("""
        <div class="block-container">
            <h2 style="
    color: #7C3AED;
    text-align: center;
    font-size: clamp(1.5rem, 5vw, 2.5rem);
    font-weight: 700;
    margin: 1rem 0;
    text-shadow: 0 1px 2px rgba(0,0,0,0.1);
">
⨀ Monad Early Checker
</h2>

<h6>Check how early your wallet joined Monad Testnet!</h6>
    """, unsafe_allow_html=True)

    wallet = st.text_input("Wallet Address", placeholder="0x.....")
    if st.button("✨ Check Wallet"):
        if wallet.lower().startswith("0x") and len(wallet) == 42:
            latest_block = get_latest_block()
            if not latest_block:
                st.error("❌ Could not connect to Monad RPC.")
            else:
                tx = get_first_tx(wallet)
                if not tx:
                    st.error("❌ No transactions found for this wallet.")
                else:
                    block = int(tx["blockNumber"])
                    date = datetime.fromtimestamp(int(tx["timeStamp"]), tz=timezone.utc).date()
                    score = calculate_score(block, latest_block)
                    tier = get_tier(block)

                    st.markdown(f"<div class='info-text'>📦First TX Block: <b>{block}</b></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='info-text'>📅 First TX Date: <b>{date}</b></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='info-text'>🏆 Tier: <b>{tier}</b></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='result-box'> Early Score: {score}%</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='color:#6B46C1; font-weight:600;'>🚀 You're earlier than ~{int(score)}% of wallets!</div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please enter a valid wallet address.")

    st.markdown("""</div>""", unsafe_allow_html=True)
