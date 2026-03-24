"""Streamlit chat UI for the Client Meeting Brief agent, with Cognito auth."""

import streamlit as st
from streamlit_cognito_auth import CognitoAuthenticator

import agent

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="Client Meeting Brief", page_icon="📋")

# ── Cognito authentication ───────────────────────────────────────────────────
# Store secrets in .streamlit/secrets.toml (never commit this file)

authenticator = CognitoAuthenticator(
    pool_id=st.secrets["COGNITO_POOL_ID"],
    app_client_id=st.secrets["COGNITO_APP_CLIENT_ID"],
    app_client_secret=st.secrets["COGNITO_APP_CLIENT_SECRET"],
)

is_logged_in = authenticator.login()
if not is_logged_in:
    st.stop()

# ── Sidebar ──────────────────────────────────────────────────────────────────

st.sidebar.title("📋 Meeting Brief")
st.sidebar.write(f"Logged in as **{authenticator.get_username()}**")
if st.sidebar.button("Logout"):
    authenticator.logout()

# ── Chat UI ──────────────────────────────────────────────────────────────────

st.title("Client Meeting Brief Generator")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Which company do you want a brief for?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            agent._init_agents()
            result = agent._orchestrator(f"Prepare a client meeting brief. {prompt}")
            response = str(result)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
