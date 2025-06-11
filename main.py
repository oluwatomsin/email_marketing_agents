import streamlit as st
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Welcome to AI Email Generation.",
    layout="wide",
)

# Get credentials from secrets
CREDENTIALS = st.secrets["credentials"]

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Check if a timestamp exists; if not, create one
if 'session_start' not in st.session_state:
    st.session_state['session_start'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Login screen
if not st.session_state.authenticated:
    st.title("🔐 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == CREDENTIALS.username and password == CREDENTIALS.password:
            st.success("✅ Login successful!")
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# Main app content (visible only after login)
else:
    st.sidebar.success("✅ You are logged in!")
    st.title("This is a Multi-Page App 🎨")
    st.write("Select a page from the sidebar to get started.")
    st.info(f"📅 Session started at: {st.session_state['session_start']}")

    # Optional: Add logout button in the sidebar
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
