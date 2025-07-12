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
st.set_page_config(page_title="Monad Early Checker", page_icon="🚀", layout="centered")

# === CSS Styling ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 50%, #6D28D9 100%);
        color: white;
        font-family: 'Inter', sans-serif;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        margin: 0;
        padding: 0;
    }

    .block-container {
        max-width: 600px;
        width: 90%;
        padding: 1.5rem;
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        color: #1F2937;
        animation: fadeIn 0.5s ease-in-out;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin: 7rem auto;
        transform: none;
    }

    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    .title {
        color: #7C3AED; /* Base purple for Monad */
        font-size: clamp(2rem, 5vw, 3rem); /* Slightly larger for better impact */
        font-weight: 800; /* Bold weight for emphasis */
        margin-bottom: 0.5rem;
        display: inline-block; /* Ensure animation applies */
        --purple: #7C3AED; /* Base purple */
        --glow-purple: #7C3AED; /* Lighter purple for glow effect */
        --speed: 1200ms; /* Match the breath animation speed */
        animation: breath calc(var(--speed)) ease calc(var(--index, 0) * 100ms) infinite alternate;
    }

    @keyframes breath {
        from {
            animation-timing-function: ease-out;
            transform: scale(1);
            text-shadow: none;
        }
        to {
            transform: scale(1.25) translateY(-5px) perspective(1px);
            text-shadow: 0 0 20px var(--glow-purple); /* Purple glow effect */
            animation-timing-function: ease-in-out;
        }
    }

    .subtitle {
        color: #6D28D9;
        font-size: clamp(0.9rem, 3vw, 1rem);
        margin-bottom: 1.5rem;
    }

 section[data-testid="stTextInput"] {
    width: 100%;
    display: flex;
    justify-content: center;
    flex-direction: column; /* Ensures label is above input */
    align-items: center;
}

section[data-testid="stTextInput"] > div {
    width: 100%;
    max-width: 400px;
}

section[data-testid="stTextInput"] > div > div {
    width: 100%;
}

section[data-testid="stTextInput"] > div > div > input {
    background-color: #F9FAFB;
    color: #7C3AED;
    border-radius: 10px;
    padding: 0.75rem;
    font-size: 1rem;
    border: 1px solid #E5E7EB;
    width: 100%;
    box-sizing: border-box;
    transition: border-color 0.3s ease;
}

section[data-testid="stTextInput"] label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #7C3AED;
    text-align: left;
    width: 100%;
    max-width: 400px;
}



    .stButton > button {
        background-color: #7C3AED;
        color: white;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border: none;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        display: block;
        margin: 1rem auto 0;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(124, 58, 237, 0.3);
    }

    .result-box {
        font-size: clamp(1.8rem, 5vw, 2.5rem);
        font-weight: 800;
        color: #7C3AED;
        margin-top: 1rem;
        animation: popIn 0.3s ease;
    }

    @keyframes popIn {
        0% { transform: scale(0.95); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    .info-text {
        font-size: clamp(0.95rem, 3vw, 1.1rem);
        font-weight: 500;
        color: #6D28D9;
        margin: 0.5rem 0;
    }

    .loading-spinner {
        border: 4px solid #E5E7EB;
        border-top: 4px solid #7C3AED;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 1rem auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Mobile responsiveness */
    @media screen and (max-width: 600px) {
        .block-container {
            width: 95%;
            padding: 1rem;
            margin: 1rem auto;
            transform: translateY(5%);
        }
        .title {
            font-size: clamp(1.5rem, 4vw, 2rem);
        }
        .result-box {
            font-size: clamp(1.5rem, 4vw, 2rem);
        }
    }
    </style>
""", unsafe_allow_html=True)

# === Main UI ===
with st.container():
    ##st.markdown('<div class="block-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="title" >⨀ EARLY MONAD CHECKER</h2>', unsafe_allow_html=True)  # Updated text
    st.markdown('<p class="subtitle">Check how early your wallet joined the Monad Testnet!</p>', unsafe_allow_html=True)
    st.markdown("""
    <footer>
        Made with 💜 by <a href="https://x.com/zahidaliAI" target="_blank">Zahid</a>
    </footer>
""", unsafe_allow_html=True)

    wallet = st.text_input("Wallet Address", placeholder="0x.....")
    check_button = st.button("✨ Check Wallet")

    if check_button:
        if wallet.lower().startswith("0x") and len(wallet) == 42:
            spinner_placeholder = st.empty()
            spinner_placeholder.markdown('<div class="loading-spinner"></div>', unsafe_allow_html=True)

            latest_block = get_latest_block()
            if not latest_block:
                spinner_placeholder.empty()
                st.error("❌ Could not connect to Monad RPC.")
            else:
                tx = get_first_tx(wallet)
                spinner_placeholder.empty()
                if not tx:
                    st.error("❌ No transactions found for this wallet.")
                else:
                    block = int(tx["blockNumber"])
                    date = datetime.fromtimestamp(int(tx["timeStamp"]), tz=timezone.utc).date()
                    score = calculate_score(block, latest_block)
                    tier = get_tier(block)

                    st.markdown(f"<div class='info-text'>📦 First TX Block: <b>{block}</b></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='info-text'>📅 First TX Date: <b>{date}</b></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='info-text'>🏆 Tier: <b>{tier}</b></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='result-box'>Early Score: {score}%</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='color:#6D28D9; font-weight:600;'>🚀 You're earlier than ~{int(score)}% of wallets!</div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please enter a valid wallet address.")
    st.markdown("</div>", unsafe_allow_html=True)
