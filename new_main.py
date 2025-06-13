import streamlit as st
import pandas as pd
from modules.utils import TextExtractor
from modules.agentsv2 import EmailGenerationAgentStreamlit
from modules.agentsv2 import LCEmailGenerationAgent   # new LC agent

# ---------- page / state ---------- #
st.set_page_config("Email Generator", layout="wide")
if "my_selections" not in st.session_state:
    st.session_state.my_selections = []

text_extractor = TextExtractor()

# ---------- 1 · CSV upload & enrichment ---------- #
uploaded_file = st.file_uploader("📂 Upload CSV File", type="csv")
enriched_df = None

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        if "Website" not in df.columns:
            st.error("❌ CSV must contain a 'Website' column.")
            st.stop()

        enriched_df = df.copy()
        with st.spinner("Enriching data from websites …"):
            enriched_df["Website Content"] = enriched_df["Website"].apply(
                lambda url: text_extractor.from_website(str(url))
            )
        st.success("✅ Data enrichment completed!")
    except pd.errors.EmptyDataError:
        st.error("❌ Uploaded file is empty or malformed.")
    except Exception as e:
        st.error(f"Error during data enrichment: {e}")

# ---------- 2 · Email-generation inputs ---------- #
if enriched_df is not None:
    st.markdown("### ✉️ Base Email Generation")
    col_a, col_b = st.columns([1, 2])

    # Persistent storage inside function scope
    sample_email = ""
    lc1_email = ""
    lc2_email = ""

    with col_a:
        selected_columns = st.pills(
            "🧠 Columns to include in the prompt",
            options=list(enriched_df.columns),
            selection_mode="multi",
            default=st.session_state.get("my_selections", []),
        )
        st.session_state.my_selections = selected_columns

        rules_text = st.text_area("Rules / Instructions")
        email_tmpl = st.text_area("Email Template", height=220)
        faq_docs = st.text_area("Company FAQ / Services", height=220)

        # Generate base email
        if st.button("🎯 Generate Email", key="btn_sample"):
            row = enriched_df.iloc[0].to_dict()
            agent = EmailGenerationAgentStreamlit(
                rules=rules_text, email_template=email_tmpl, faq_docs=faq_docs
            )
            sample_email = agent.generate_email(row, selected_columns)

        if sample_email:
            st.text_area("📬 Base Email Output", value=sample_email, height=300, key="base_email_out")

    with col_b:
        st.dataframe(enriched_df, use_container_width=True)

    # ---------- LC Section ---------- #
    st.markdown("---")
    enable_lc = st.toggle("🔄 Advanced Lead-Cadence (LC) Generation (optional)")

    if enable_lc:
        row = enriched_df.iloc[0].to_dict()

        with st.expander("LC 1 settings"):
            lc1_rules = st.text_area("LC 1 Rules / Instructions", key="lc1_rules")

            if st.button("📝 Generate LC 1 Email", key="btn_lc1"):
                lc1_agent = LCEmailGenerationAgent(
                    level="LC1",
                    rules=lc1_rules,
                    faq_docs=faq_docs,
                )
                lc1_email = lc1_agent.generate_email(
                    row=row,
                    selected_fields=selected_columns,
                    original_email=sample_email,
                )

            if lc1_email:
                st.text_area("📬 LC 1 Email Output", value=lc1_email, height=300, key="lc1_email_out")

        with st.expander("LC 2 settings"):
            lc2_rules = st.text_area("LC 2 Rules / Instructions", key="lc2_rules")

            if st.button("📝 Generate LC 2 Email", key="btn_lc2"):
                lc2_agent = LCEmailGenerationAgent(
                    level="LC2",
                    rules=lc2_rules,
                    faq_docs=faq_docs,
                )
                lc2_email = lc2_agent.generate_email(
                    row=row,
                    selected_fields=selected_columns,
                    original_email=sample_email,
                )

            if lc2_email:
                st.text_area("📬 LC 2 Email Output", value=lc2_email, height=300, key="lc2_email_out")
