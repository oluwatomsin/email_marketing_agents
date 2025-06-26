import os
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from rich import print

load_dotenv()


class EmailGenerationAgentStreamlit:
    def __init__(self, rules: str, email_template: str, faq_docs: str,
                 model_name: str = "gemini-2.5-flash-preview-05-20", temperature: float = 0.1):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set OPENAI_API_KEY in .env file.")

        self.rules = rules
        self.template = email_template
        self.faq_docs = faq_docs
        self.model = ChatGoogleGenerativeAI(model=model_name, temperature=temperature,
                                            max_retries=2)

    def _build_prompt(self, fields: list[str]):
        input_vars = fields + ["instructions", "email_template", "faq_docs"]
        context_lines = [f"{field}: {{{field}}}" for field in fields]

        prompt = f"""
You are an SDR assistant generating cold outreach emails for a sales campaign.\n\n

Here is the lead information:\n
{chr(10).join(context_lines)}\n\n

Instructions for crafting the email:\n
{{instructions}}\n\n

Our Company Info and Services (for tailoring the outreach):\n
{{faq_docs}}\n\n

Use this email template as the structure:\n
{{email_template}}\n\n

Only return the final formatted email.\n
""".strip()

        return PromptTemplate(input_variables=input_vars, template=prompt)

    def generate_email(self, row: dict, selected_fields: list[str]):
        prompt = self._build_prompt(selected_fields)
        input_data = {field: row.get(field, "") for field in selected_fields}
        input_data["instructions"] = self.rules
        input_data["email_template"] = self.template
        input_data["faq_docs"] = self.faq_docs

        prompt_text = prompt.format(**input_data)
        response = self.model.invoke(prompt_text)
        return response.content.strip()



class LCEmailGenerationAgent:
    """
    Generic agent for “LC” (lead-cadence / long-copy) emails.
    Pass level='LC1' or 'LC2' (or any other tag) to embed it in the prompt.
    """

    def __init__(
        self,
        level: str,
        rules: str,
        email_template: str = None,  # made optional
        faq_docs: str = "",
        model_name: str = "gemini-2.5-flash-preview-05-20",
        temperature: float = 0.1,
    ):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "API key not found. Set OPENAI_API_KEY in your .env file."
            )

        self.level = level.upper()
        self.rules = rules
        self.template = email_template
        self.faq_docs = faq_docs
        self.model = ChatGoogleGenerativeAI(model=model_name, temperature=temperature,
                                            max_retries=2)

    def _build_prompt(self, fields: list[str]) -> PromptTemplate:
        input_vars = fields + ["instructions", "faq_docs", "lc_level"]
        if self.template:
            input_vars.append("email_template")
        input_vars.append("original_email")

        context_lines = [f"{field}: {{{field}}}" for field in fields]

        prompt = f"""
    You are a Senior SDR assistant.

    • Goal: craft a {{lc_level}} cold-outreach email that converts.
    • Audience: busy decision makers — keep it concise and value-focused.

    Lead information:
    {chr(10).join(context_lines)}

    Previous email sent in this sequence:
    {{original_email}}

    Guidelines for this {{lc_level}} email:
    {{instructions}}

    Our company background & services:
    {{faq_docs}}
    """.strip()

        if self.template:
            prompt += "\n\nFollow this structural template:\n{{email_template}}"

        prompt += "\n\nReturn **only** the completed message — no commentary."

        return PromptTemplate(input_variables=input_vars, template=prompt)

    def generate_email(self, row: dict, selected_fields: list[str], original_email: str = "") -> str:
        prompt = self._build_prompt(selected_fields)

        variables = {field: row.get(field, "") for field in selected_fields}
        variables.update({
            "instructions": self.rules,
            "faq_docs": self.faq_docs,
            "lc_level": self.level,
            "original_email": original_email,
        })
        if self.template:
            variables["email_template"] = self.template

        final_prompt = prompt.format(**variables)
        response = self.model.invoke(final_prompt)
        return response.content.strip()
