import requests
import streamlit as st
import os

# Docker compatible BASE URL
BASE_URL = os.getenv(
    "BASE_URL",
    "http://localhost:8000"
)

def get_auth_headers():

    token = st.session_state.get("token")

    if not token:
        return None

    return {
        "Authorization": f"Bearer {token}"
    }


def get_dashboard():

    headers = get_auth_headers()

    if not headers:
        return {"error": "Not authenticated"}

    try:
        response = requests.get(
            f"{BASE_URL}/dashboard",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Unauthorized"}

    except Exception:
        return {"error": "Backend unreachable"}


def get_history():

    headers = get_auth_headers()

    if not headers:
        return []

    try:
        response = requests.get(
            f"{BASE_URL}/history",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return []

    except Exception:
        return []


def get_hedge_logs():

    headers = get_auth_headers()

    if not headers:
        return []

    try:
        response = requests.get(
            f"{BASE_URL}/hedge-logs",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return []

    except Exception:
        return []
