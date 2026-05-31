import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Acme Enterprise Assistant",
    layout="wide"
)
API_BASE_URL = "http://api:8000"
KEYCLOAK_TOKEN_URL = "http://keycloak:8080/realms/acme/protocol/openid-connect/token"
st.title("Acme Enterprise Assistant")

if "token" not in st.session_state:
    st.session_state.token = None

with st.sidebar:
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        payload = {
            "client_id": "acme-api",
            "username": username,
            "password": password,
            "grant_type": "password"
        }
        response = requests.post(
            KEYCLOAK_TOKEN_URL,
            data=payload
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state.token = token
            st.success("Login successful")
        else:
            st.error("Login failed")

    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.rerun()
    if st.sidebar.button("Clear Conversation"):
        response = requests.delete(
            f"{API_BASE_URL}/clear_user_cache",
            headers=headers
        )
        if response.status_code == 200:
            st.success("Conversation cleared")
        else:
            st.error(response.text)
    st.sidebar.markdown("---")
    if st.sidebar.button("View Traces"):
        response = requests.get(f"{API_BASE_URL}/traces", headers=headers)
        if response.status_code == 200:
            traces = response.json()["traces"]
            if traces:
                st.subheader("Trace Dashboard")
                st.dataframe(pd.DataFrame(traces))
            else:
                st.error("No traces found")
        else:
            st.error(response.text)
        st.sidebar.markdown("---")

if st.session_state.token:
    st.subheader("Chat")
    user_query = st.text_area("Enter your query")
    if st.button("Send Query"):
        headers = {
            "Authorization":
                f"Bearer {st.session_state.token}"
        }
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": user_query
            },
            headers=headers
        )
        if response.status_code == 200:
            result = response.json()
            st.markdown("### Assistant Response")
            st.write(result["response"])
        else:
            st.error(response.text)
