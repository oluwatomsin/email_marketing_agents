import os
import yaml
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


class AEAgentBase:
    def __init__(self, config_path: str, instruction_key: str, model_name: str = "gemini-2.5-flash-preview-05-20", temperature: float = 0.1):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set OPENAI_API_KEY in .env file.")

        self.instruction_key = instruction_key
        self.instructions = self._get_instructions()
        # self.model = ChatOpenAI(api_key=self.api_key, model=model_name, temperature=temperature)
        self.model = ChatGoogleGenerativeAI(model=model_name, temperature=temperature,
                                            max_retries=2)
        self.prompt = self._build_prompt()

    def _get_instructions(self):
        if self.instruction_key not in self.config["instructions"]:
            raise KeyError(f"Instruction key '{self.instruction_key}' not found in YAML config.")
        return self.config["instructions"][self.instruction_key]

    def _build_prompt(self):
        raise NotImplementedError("Subclasses must implement _build_prompt")

    def generate(self, **kwargs):
        prompt_text = self.prompt.format(**kwargs)
        response = self.model.invoke(prompt_text)
        return response.content.strip()


class SDRAgent1(AEAgentBase):
    def _build_prompt(self):
        return PromptTemplate(
            input_variables=["job_url", "job_post", "target_company_homepage", "salaria_homepage_faq", "lead_info"],
            template="""
You are a helpful SDR assistant for Salaria.

Job URL: {job_url}
Job Post: {job_post}
Lead Info: {lead_info}
Target Company Homepage: {target_company_homepage}
Our services and keywords: {salaria_homepage_faq}

Instructions:
{instructions}

Craft the opening paragraph for outreach. Only return the output text and adhere to the character limits.
Please adhere strictly to the instructions provided.
""".strip()
        )

    def generate(self, job_url, job_post, target_company_homepage, salaria_homepage_faq, lead_info):
        return super().generate(
            job_url=job_url,
            job_post=job_post,
            target_company_homepage=target_company_homepage,
            salaria_homepage_faq=salaria_homepage_faq,
            lead_info=lead_info,
            instructions=self.instructions
        )


class SDRAgent2(AEAgentBase):
    def _build_prompt(self):
        return PromptTemplate(
            input_variables=["paragraph_1", "job_url", "job_post", "target_company_homepage", "salaria_homepage_faq", "lead_info"],
            template="""
You are a helpful SDR assistant continuing a message for Salaria.

Paragraph 1 (context): {paragraph_1}
Job URL: {job_url}
Job Post: {job_post}
Target Lead Info: {lead_info}
Target Company Homepage: {target_company_homepage}
our_services_and_keywords: {salaria_homepage_faq}

Instructions:
{instructions}

Write the second paragraph, continuing naturally. Only return the paragraph and adhere to the character limits.
Please adhere strictly to the instructions provided.
""".strip()
        )

    def generate(self, paragraph_1, job_url, job_post, target_company_homepage, salaria_homepage_faq, lead_info):
        return super().generate(
            paragraph_1=paragraph_1,
            job_url=job_url,
            job_post=job_post,
            target_company_homepage=target_company_homepage,
            salaria_homepage_faq=salaria_homepage_faq,
            lead_info=lead_info,
            instructions=self.instructions
        )


class SDRAgent3(AEAgentBase):
    def _build_prompt(self):
        return PromptTemplate(
            input_variables=["paragraph_1", "paragraph_2", "job_url", "job_post", "target_company_homepage", "salaria_homepage_faq", "lead_info", "second_lead"],
            template="""
You are a helpful SDR assistant finishing a message for Salaria.

Paragraph 1: {paragraph_1}\n
Paragraph 2: {paragraph_2}\n
Job URL: {job_url}\n
Job Post: {job_post}\n
Target Lead Info: {lead_info}\n

Other leads that have been reached out to: {second_lead}\n
Target Company Homepage: {target_company_homepage}\n
our_services_and_keywords: {salaria_homepage_faq}\n\n

Instructions:\n
{instructions}\n\n

Write the final paragraph to conclude the outreach. Only return the paragraph and adhere to the character limits.
Please adhere strictly to the instructions provided.
""".strip()
        )

    def generate(self, paragraph_1, paragraph_2, job_url, job_post, target_company_homepage, salaria_homepage_faq, lead_info, second_lead):
        return super().generate(
            paragraph_1=paragraph_1,
            paragraph_2=paragraph_2,
            job_url=job_url,
            job_post=job_post,
            target_company_homepage=target_company_homepage,
            salaria_homepage_faq=salaria_homepage_faq,
            lead_info=lead_info,
            instructions=self.instructions,
            second_lead=second_lead
        )

class CallLineAgent(AEAgentBase):
    def _build_prompt(self):
        return PromptTemplate(
            input_variables=["company_info", "email_text", "job_post", "lead_info"],
            template="""
You are a helpful SDR assistant preparing a phone call script for cold outreach.

Company Info: {company_info}
Full Email Text: {email_text}
Target Lead info: {lead_info}

Job Post: {job_post}

Instructions:
{instructions}

Using the provided email and company information and job post, generate a phone call script following the provided instructions.
Please adhere strictly to the instructions provided.
""".strip()
        )

    def generate(self, company_info, email_text, job_post, lead_info):
        return super().generate(
            company_info=company_info,
            email_text=email_text,
            instructions=self.instructions,
            job_post=job_post,
            lead_info=lead_info
        )


class LC1Agent(AEAgentBase):
    def _build_prompt(self):
        return PromptTemplate(
            input_variables=["full_email", "company_info", "lead_info", 'salaria_homepage_faq'],
            template="""
You are an advanced agent for salaria that is responsible for crafting outreach messages.

full_email:
{full_email}

lead's Company Info:
{company_info}

our_services_and_keywords: 
{salaria_homepage_faq}

Target Lead Info:
{lead_info}

Instructions:
{instructions}

Based on the information above, create an outreach message following the provided instructions. 
Focus on personalization, tone, and strategic fit. Return only the message and do not include any dashes.
Please adhere strictly to the instructions provided.
""".strip()
        )

    def generate(self, full_email, company_info, lead_info, salaria_homepage_faq):
        return super().generate(
            full_email=full_email,
            company_info=company_info,
            lead_info=lead_info,
            instructions=self.instructions,
            salaria_homepage_faq=salaria_homepage_faq,
        )


class LC2Agent(AEAgentBase):
    def _build_prompt(self):
        return PromptTemplate(
            input_variables=["full_email", "lc1_output", "job_post", "company_info", "lead_info", "salaria_homepage_faq"],
            template="""
You are a senior SDR assistant refining a sales outreach message for Salaria.

Original Email Text (full_email):
{full_email}

LC1 Agent Output:
{lc1_output}

Job Post:
{job_post}

Lead's Company Info:
{company_info}

Target Lead Info:
{lead_info}

our_services_and_keywords:
{salaria_homepage_faq}

Instructions:
{instructions}

Using the original email and LC1 output as context, refine or rewrite the email to improve personalization, clarity, tone, and alignment with Salaria’s goals. Focus on strategic fit. 
Return only the finalized email. Do not include any extraneous commentary.
""".strip()
        )

    def generate(self, full_email, lc1_output, job_post, company_info, lead_info, salaria_homepage_faq):
        return super().generate(
            full_email=full_email,
            lc1_output=lc1_output,
            job_post=job_post,
            company_info=company_info,
            lead_info=lead_info,
            salaria_homepage_faq=salaria_homepage_faq,
            instructions=self.instructions
        )


class SubjectLineAgent(AEAgentBase):
    def _build_prompt(self):
        return PromptTemplate(
            input_variables=["company", "Full Email"],
            template="""
You are an expert at crafting Subject Lines for email. I want you to create a single subject line for email provided.
    Please make sure that the subject line sounds like it was written by a human.

    Here are a few examples:
    1. Supporting MindStaq’s Sales Growth Strategy
    2. Supporting Your Sales Growth at Courie
    3. Supporting Weights & Biases' Sales Growth

Original Email Text (full_email):
{full_email}

Company Name:
{company}

Instructions:
{instructions}

Using the original email and company name as context.
Return only the subject line.
""".strip()
        )

    def generate(self, full_email, company):
        return super().generate(
            full_email=full_email,
            company=company,
            instructions=self.instructions
        )
