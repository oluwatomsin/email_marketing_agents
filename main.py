import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Welcome to AI Email Generation.",
    layout="wide",
)

# Check if a timestamp exists; if not, create one
if 'session_start' not in st.session_state:
    st.session_state['session_start'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.title("This is a Multi-Page App 🎨")
st.write("Select a page from the sidebar to get started.")
