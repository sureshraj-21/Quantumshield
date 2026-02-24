import streamlit as st
import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

st.set_page_config(layout="wide")

# ---------------- LOGIN ----------------

if "token" not in st.session_state:

    st.title("🤖 AI Financial Intelligence")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password}
        )

        if response.status_code == 200:
            st.session_state["token"] = response.json()["access_token"]
            st.success("AI Agent: Welcome Back 👋")
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

st.title("🤖 AI Financial Complete Portfolio Optimizer")

st.success("AI Agent: Select a stock to analyze 📈")

stock = st.selectbox(
    "Select Stock",
    ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
)

if st.button("Analyze Stock"):

    response = requests.get(
        f"{BASE_URL}/analyze-stock/{stock}",
        headers=headers
    )

    if response.status_code != 200:
        st.error("Analysis Failed")
        st.stop()

    data = response.json()

    if "error" in data:
        st.error(data["error"])
        st.stop()

    # -------------------------
    # MARKET METRICS
    # -------------------------
    st.subheader("📊 Market Analysis")

    col1, col2 = st.columns(2)

    col1.metric("Current Price", f"₹ {round(data['current_price'],2)}")
    col2.metric("Predicted Return",
                f"{round(data['predicted_return']*100,2)}%")

    st.metric("Sharpe Ratio", round(data["sharpe"],2))
    st.metric("Volatility", round(data["volatility"],4))
    st.metric("Market Regime", data["regime"])
    st.metric("BSI", round(data["bsi"],2))
    st.metric("CPS", round(data["cps"],2))

    # -------------------------
    # GHOST HEDGE (MUST BE INSIDE)
    # -------------------------
    st.subheader("🛡 Ghost Hedge System")

    if data["hedge_status"] == "ACTIVE":
        st.error("🔴 Hedge ACTIVE – Capital Protected")
    else:
        st.success("🟢 Hedge INACTIVE – Normal Exposure")

    # -------------------------
    # MONTE CARLO
    # -------------------------
    st.subheader("🎲 Monte Carlo Forecast")

    st.metric("Expected Growth",
              round(data["monte_carlo_expected"],2))

    st.metric("₹10,000 Expected Value",
              f"₹ {round(data['investment_10000_expected'],2)}")

    st.metric("₹10,000 Worst Case",
              f"₹ {round(data['investment_10000_worst'],2)}")

    # -------------------------
    # AI FINAL VERDICT
    # -------------------------
    st.subheader("🤖 AI Final Verdict")

    if data["decision"] == "BUY":
        st.success("🟢 AI Suggests BUY")
    elif data["decision"] == "HOLD":
        st.warning("🟡 AI Suggests HOLD")
    else:
        st.error("🔴 AI Suggests AVOID")