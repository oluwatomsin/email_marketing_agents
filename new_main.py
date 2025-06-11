import streamlit as st
import pandas as pd
from modules.utils import TextExtractor


# Initialize extractors and agents
text_extractor = TextExtractor()
from modules.agentsv2 import EmailGenerationAgentStreamlit

st.set_page_config(page_title="Email Generator", layout="wide")

# Title
st.title("📧 Email Generation Tool")

# Standalone File Uploader
uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])

# Load DataFrame once and reuse
enriched_df = None
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        enriched_df = df.copy()
        enriched_df["Website Content"] = enriched_df["Website"].apply(lambda url: text_extractor.from_website(str(url)))
        print("✅ Data enrichment completed.")
    except pd.errors.EmptyDataError:
        st.error("❌ Uploaded file is empty or not properly formatted.")
    except Exception as e:
        st.error("Error during data enrichment")


# Rules and Templates Section
col1, col2 = st.columns([1, 2])

with col1:
    rules_text = st.text_area("Enter Email Generation Rules here ...")
    email_template = st.text_area("Enter Email Template here ...", height=480)
    faq_docs = st.text_area("Enter Your company Info here ...", height=480)

    if st.toggle("LC 1"):
        st.text_area("Enter LC 1 Generation Rules here ...")
        st.text_area("Enter LC 1 Email Template here ...")

    if st.toggle("LC 2"):
        st.text_area("Enter LC 2 Generation Rules here ...")
        st.text_area("Enter LC 2 Email Template here ...")

    if enriched_df is not None:
        options = list(enriched_df.columns)
        my_selections = st.pills("🧠 Select the columns used for email context", options, selection_mode="multi", default=[])
        print(my_selections)

with col2:
    if enriched_df is None:
        st.info("Please upload a CSV file to begin.")

# Proceed if DataFrame is ready
if enriched_df is not None:
    st.markdown("---")
    if st.button("🎯 Generate Sample Email"):
        sample_row = enriched_df.iloc[0].to_dict()
        agent = EmailGenerationAgentStreamlit(rules=rules_text, email_template=email_template, faq_docs=faq_docs)
        email = agent.generate_email(sample_row, my_selections)
        st.text_area("📬 Sample Email Output", value=email, height=300)
