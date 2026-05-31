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
    if st.sidebar.button("Open Trace Viewer"):
        response = requests.get(
            f"{API_BASE_URL}/traces",
            headers=headers
        )
        if response.status_code == 200:
            traces = response.json()["traces"]
            if traces:
                st.subheader("Agent Trace Viewer")
                st.info(
                    """
                    This custom trace viewer provides visibility into:
                    - Planner decisions
                    - MCP tool executions
                    - Skill selection
                    """
                )
                df = pd.DataFrame(traces)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Agent Decisions",
                        len([
                            t for t in traces
                            if t.get("type") == "agent"
                        ])
                    )
                with col2:
                    st.metric(
                        "Tool Executions",
                        len([
                            t for t in traces
                            if t.get("type") == "tool_execution"
                        ])
                    )
                with col3:
                    st.metric(
                        "Skill Executions",
                        len([
                            t for t in traces
                            if t.get("type") == "skill"
                        ])
                    )
                tool_traces = [
                    t for t in traces
                    if t.get("type") == "tool_execution"
                ]
                if tool_traces:
                    tool_df = pd.DataFrame(tool_traces)
                    if "tool_name" in tool_df.columns:
                        st.subheader("Tool Usage Statistics")
                        st.bar_chart(
                            tool_df["tool_name"].value_counts()
                        )
                st.subheader("Latest Event")
                st.json(traces[-1])
                st.subheader("Trace Events")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No traces found")
        else:
            st.error(response.text)
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
