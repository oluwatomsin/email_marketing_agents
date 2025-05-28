import streamlit as st
import pandas as pd
import logging
import traceback
import os
from dotenv import load_dotenv
from modules.utils import TextExtractor, generate_email_subject
from modules.agents import SDRAgent1, SDRAgent2, SDRAgent3, CallLineAgent, LC1Agent, LC2Agent

# Setup logging
logging.basicConfig(
    filename="../sdr_app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")


# Helper function to print logs to terminal (for Streamlit visibility)
def log_and_print(message: str, level="info"):
    log_func = getattr(logger, level, logger.info)
    log_func(message)
    try:
        os.write(1, f"{message}\n".encode())
    except Exception:
        pass

# Load environment variables
load_dotenv()
log_and_print("✅ Environment variables loaded.")

# Initialize extractors and agents
text_extractor = TextExtractor()
log_and_print("🧠 TextExtractor initialized.")

agent1 = SDRAgent1(config_path="config/instructions_v2.yml", instruction_key="sdr_1")
agent2 = SDRAgent2(config_path="config/instructions_v2.yml", instruction_key="sdr_2")
agent3 = SDRAgent3(config_path="config/instructions_v2.yml", instruction_key="sdr_3")
call_agent = CallLineAgent(config_path="config/instructions_v2.yml", instruction_key="call_line")
lc1_agent = LC1Agent(config_path="config/instructions_v2.yml", instruction_key="lc1")
lc2_agent = LC2Agent(config_path="config/instructions_v2.yml", instruction_key="lc2")
log_and_print("🤖 All agents initialized.")

st.title("📧 AI-Powered SDR Email Generator")

uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv")

@st.cache_data(show_spinner="🔍 Enriching data with companies websites content ...")
def enrich_dataset(data: pd.DataFrame) -> pd.DataFrame:
    log_and_print("🔍 Starting data enrichment...")
    enriched_df = data.copy()
    try:
        enriched_df["Website Content"] = enriched_df["Website"].apply(lambda url: text_extractor.from_website(str(url)))
        enriched_df["Lead_info"] = (
            enriched_df["First Name"].fillna('') + " " +
            enriched_df["Last Name"].fillna('') + " - " +
            enriched_df["Title"].fillna('')
        )
        log_and_print("✅ Data enrichment completed.")
        return enriched_df
    except Exception as e:
        log_and_print(f"❌ Error during data enrichment: {e}", level="error")
        traceback.print_exc()
        raise

if uploaded_file:
    log_and_print("📄 File uploaded.")
    try:
        df = pd.read_csv(uploaded_file)
        df = df
        log_and_print("📥 CSV read successfully.")

        required_columns = {"Job post Link", "Website", "First Name", "Second_Lead_info", "Company",
                            "Last Name", "Title", "Job Post", "Job post Link", "HQ Phone", "Direct Phone", "Email Address"}

        if not all(col in df.columns for col in required_columns):
            log_and_print("❗ CSV missing required columns.", level="error")
            missing_columns = required_columns.difference(set(df.columns))
            st.error(f"The CSV is missing the following columns:\n\n {", \n\n".join(missing_columns)}")
        else:
            st.info("⏳ Step 1: Enriching with company's website homepage content")
            df = enrich_dataset(df)
            st.success("✅ Data enrichment completed!")
            st.subheader("📄 Preview Enriched Data")
            st.warning('In some cases, the bot might not be able to automatically get the information from some '
                       'websites. Cross check the **["Website Content"]** column for such cases and kindly replace the '
                       'data where and error occurred.', icon="⚠️")
            df = st.data_editor(df)
            if st.button("🚀 Generate AI Email Paragraphs"):
                log_and_print("🚀 AI Email generation started.")
                st.info("⏳ Generating AI Emails...")

                def generate_all_paragraphs(row):
                    try:
                        log_and_print(f"✉️ Generating email for: {row['First Name']} {row['Last Name']}")
                        p1 = agent1.generate(
                            job_url=row["Job post Link"],
                            job_post=row["Job Post"],
                            target_company_homepage=row["Website Content"],
                            salaria_homepage_faq=agent1.config["instructions"].get("faq", ""),
                            lead_info=row['Lead_info']
                        )

                        p2 = agent2.generate(
                            paragraph_1=p1,
                            job_url=row["Job post Link"],
                            job_post=row["Job Post"],
                            target_company_homepage=row["Website Content"],
                            salaria_homepage_faq=agent2.config["instructions"].get("faq", ""),
                            lead_info=row['Lead_info']
                        )

                        p3 = agent3.generate(
                            paragraph_1=p1,
                            paragraph_2=p2,
                            job_url=row["Job post Link"],
                            job_post=row["Job Post"],
                            target_company_homepage=row["Website Content"],
                            salaria_homepage_faq=agent3.config["instructions"].get("faq", ""),
                            lead_info=row['Lead_info'],
                            second_lead=row['Second_Lead_info']
                        )

                        full_email = f"Hi {row.get('First Name', '').strip()}\n\n{p1}\n\n{p2}\n\n{p3}".strip()

                        call_line = call_agent.generate(
                            email_text=full_email,
                            company_info=row["Website Content"],
                            job_post=row["Job Post"],
                            lead_info=row['Lead_info']
                        )

                        lc1_output = lc1_agent.generate(
                            full_email=full_email,
                            company_info=row["Website Content"],
                            lead_info=row['Lead_info'],
                            salaria_homepage_faq=agent3.config["instructions"].get("faq", "")
                        )

                        lc2_output = lc2_agent.generate(
                            full_email=full_email,
                            company_info=row["Website Content"],
                            lead_info=row['Lead_info'],
                            lc1_output=lc1_output,
                            job_post=row["Job Post"],
                            salaria_homepage_faq=agent3.config["instructions"].get("faq", "")
                        )

                        return pd.Series([p1, p2, p3, full_email, call_line, lc1_output, lc2_output])

                    except Exception as e:
                        log_and_print(f"❌ Error generating paragraphs for {row.get('First Name', 'N/A')}: {e}", level="error")
                        traceback.print_exc()
                        return pd.Series([f"[Error] {e}", "", "", "", "", "", ""])

                df[[
                    "AI Email Paragraph 1",
                    "AI Email Paragraph 2",
                    "AI Email Paragraph 3",
                    "Full Email",
                    "Call Line",
                    "LC1 Output",
                    "LC2 Output"
                ]] = df.apply(generate_all_paragraphs, axis=1)

                def generate_full_email(row):
                    greeting = f"Hi {row.get('First Name', '').strip()}"
                    parts = [
                        greeting,
                        row.get("AI Email Paragraph 1", "").strip(),
                        row.get("AI Email Paragraph 2", "").strip(),
                        row.get("AI Email Paragraph 3", "").strip()
                    ]
                    return "\n\n".join(part for part in parts if part)

                df["Full Email"] = df.apply(generate_full_email, axis=1)

                # Generating email subject line
                df["Subject Line"] = df['Full Email'].apply(generate_email_subject)

                st.success("✅ AI Emails generated!")
                log_and_print("✅ AI Email generation completed successfully.")

                st.subheader("📧 Preview of Generated Emails, Call Lines & LC1/LC2 Output")
                st.dataframe(df[[
                    "Company",
                    "Website",
                    "Lead_info",
                    "Email Address",
                    "Subject Line",
                    "Full Email",
                    "Call Line",
                    "LC1 Output",
                    "LC2 Output",
                    "HQ Phone",
                    "Direct Phone"
                ]].head(10))

                # Download button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Enhanced CSV with Emails, Call Lines, LC1 & LC2 Output",
                    data=csv,
                    file_name='enhanced_email_call_lc_data.csv',
                    mime='text/csv',
                )
                log_and_print("📥 CSV download button rendered.")
    except Exception as e:
        log_and_print(f"🔥 Unhandled exception: {e}", level="error")
        traceback.print_exc()
        st.error(f"Something went wrong: {e}")
