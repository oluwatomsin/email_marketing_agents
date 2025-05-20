import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from modules.utils import TextExtractor
from modules.agents import SDRAgent1, SDRAgent2, SDRAgent3, CallLineAgent, LC1Agent, LC2Agent
# import swifter

# Load environment variables
load_dotenv()

# Initialize extractors
text_extractor = TextExtractor()

# Initialize SDR paragraph agents
agent1 = SDRAgent1(config_path="config/instructions_v2.yml", instruction_key="sdr_1")
agent2 = SDRAgent2(config_path="config/instructions_v2.yml", instruction_key="sdr_2")
agent3 = SDRAgent3(config_path="config/instructions_v2.yml", instruction_key="sdr_3")
call_agent = CallLineAgent(config_path="config/instructions_v2.yml", instruction_key="call_line")
lc1_agent = LC1Agent(config_path="config/instructions_v2.yml", instruction_key="lc1")
lc2_agent = LC2Agent(config_path="config/instructions_v2.yml", instruction_key="lc2")

st.title("📧 AI-Powered SDR Email Generator")
# This is done
uploaded_file = st.file_uploader("📤 Upload your CSV file", type="csv")


@st.cache_data(show_spinner="🔍 Enriching data with companies websites content ...")
def enrich_dataset(data: pd.DataFrame) -> pd.DataFrame:
    enriched_df = data.copy()
    enriched_df["Website Content"] = enriched_df["Website"].apply(lambda url: text_extractor.from_website(str(url)))
    # 1. Create "Lead_info" column by combining First Name, Last Name, and Title
    enriched_df["Lead_info"] = enriched_df["First Name"].fillna('') + " " + enriched_df["Last Name"].fillna('') + " - " + enriched_df["Title"].fillna('')
    return enriched_df


if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = df.head(3)  # Limit for testing

    required_columns = ["Job post Link", "Website", "First Name", "Second_Lead_info",
                        "Last Name", "Title", "Job Post", "Job post Link"]
    if not all(col in df.columns for col in required_columns):
        st.error("The CSV must contain the following columns: 'Title', 'Job post Link', 'Job Post', 'Job post Link', "
                 "'fellow title' ,'Website', and 'Second_Lead_info'")
    else:
        st.info("⏳ Step 1: Enriching with company's website homepage content")

        df = enrich_dataset(df)

        st.success("✅ Data enrichment completed!")

        st.subheader("📄 Preview Enriched Data")
        st.dataframe(df[["Job post Link", "Website", "Job Post", "Website Content", "Lead_info", "Second_Lead_info"]].head(10))

        if st.button("🚀 Generate AI Email Paragraphs"):
            st.info("⏳ Generating AI Emails...")


            def generate_all_paragraphs(row):
                try:
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
                greeting = f"Hello {row.get('First Name', '').strip()}"
                parts = [
                    greeting,
                    row.get("AI Email Paragraph 1", "").strip(),
                    row.get("AI Email Paragraph 2", "").strip(),
                    row.get("AI Email Paragraph 3", "").strip()
                ]
                return "\n\n".join(part for part in parts if part)

            df["Full Email"] = df.apply(generate_full_email, axis=1)

            st.success("✅ AI Emails generated!")

            st.subheader("📧 Preview of Generated Emails, Call Lines & LC1/LC2 Output")
            st.dataframe(df[[
                "Job post Link",
                "Website",
                "Lead_info",
                # "AI Email Paragraph 1",
                # "AI Email Paragraph 2",
                # "AI Email Paragraph 3",
                "Full Email",
                "Call Line",
                "LC1 Output",
                "LC2 Output"
            ]].head(10))

            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Enhanced CSV with Emails, Call Lines, LC1 & LC2 Output",
                data=csv,
                file_name='enhanced_email_call_lc_data.csv',
                mime='text/csv',
            )
