import os
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from rich import print

load_dotenv()


class EmailGenerationAgentStreamlit:
    def __init__(self, rules: str, email_template: str, faq_docs: str,
                 model_name: str = "gpt-4.1-mini", temperature: float = 0.7):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set OPENAI_API_KEY in .env file.")

        self.rules = rules
        self.template = email_template
        self.faq_docs = faq_docs
        self.model = ChatOpenAI(api_key=self.api_key, model=model_name, temperature=temperature)

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


class LinkedInConnectionAgent:
    """
    A class to generate personalized LinkedIn connection requests (LC1 and LC2)
    using an OpenAI large language model. Each message is generated exclusively
    based on dynamic specific instructions for its type (LC1 or LC2).
    """
    def __init__(self,
                 model_name: str = "gpt-4o-mini",
                 temperature: float = 0.7):
        """
        Initializes the LinkedInConnectionAgent.

        Args:
            model_name (str): The name of the OpenAI model to use.
            temperature (float): Controls the creativity of the model (0.0-1.0).
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set OPENAI_API_KEY in your .env file.")

        self.model = ChatOpenAI(api_key=self.api_key, model=model_name, temperature=temperature)


    def _build_prompt(self, fields: list[str]):
        """
        Constructs the PromptTemplate for the LLM.
        The entire message generation is based on specific instructions for the connection type.

        Args:
            fields (list[str]): A list of lead data fields to include in the prompt.

        Returns:
            PromptTemplate: The Langchain PromptTemplate object.
        """
        # 'specific_instructions' is now the only dynamic instruction variable
        input_vars = fields + ["specific_instructions", "connection_type_name"]
        context_lines = [f"{field}: {{{field}}}" for field in fields]

        prompt_str = f"""
You are an AI assistant specialized in crafting concise and effective LinkedIn connection requests.\n
Your goal is to help users connect with relevant professionals by generating the full message.\n\n

Here is the prospect's information:\n
{chr(10).join(context_lines)}\n\n

Instructions for this connection request type ({{connection_type_name}}):\n
{{specific_instructions}}\n\n

Ensure the generated message is a complete LinkedIn connection request note, including a suitable greeting and closing,
and is within LinkedIn's character limits (typically ~300 characters, but aim for conciseness).\n
Only return the final formatted LinkedIn connection request note.
If you cannot generate a meaningful request based on the provided data and instructions, return an empty string or a placeholder indicating failure.
""".strip()

        return PromptTemplate(input_variables=input_vars, template=prompt_str)


    def generate_connection_request(self,
                                    row: dict,
                                    selected_fields: list[str],
                                    connection_type: str, # 'LC1' or 'LC2' (for naming in prompt)
                                    specific_instructions: str) -> str: # Dynamically passed
        """
        Generates a personalized LinkedIn connection request.

        Args:
            row (dict): A dictionary containing the prospect's data (e.g., name, company, shared_connection).
            selected_fields (list[str]): A list of keys from 'row' to use in the prompt.
            connection_type (str): The type of connection request being generated ('LC1' or 'LC2').
                                   Used primarily for context in the prompt.
            specific_instructions (str): Detailed instructions for this specific connection type (LC1 or LC2).

        Returns:
            str: The generated LinkedIn connection request message.
        """
        if connection_type not in ['LC1', 'LC2']:
            raise ValueError("Invalid connection_type. Must be 'LC1' or 'LC2'.")

        # Build the prompt structure
        prompt = self._build_prompt(selected_fields)

        # Prepare input data for the prompt
        input_data = {field: row.get(field, "") for field in selected_fields}
        input_data["specific_instructions"] = specific_instructions
        input_data["connection_type_name"] = connection_type # Pass the type name to the prompt

        prompt_text = prompt.format(**input_data)
        response = self.model.invoke(prompt_text)
        return response.content.strip()