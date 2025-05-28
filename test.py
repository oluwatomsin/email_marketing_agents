from openai import OpenAI
from dotenv import load_dotenv
from modules.utils import generate_email_subject

load_dotenv()

client = OpenAI()

# contexts = "You are a helpful assistant that structures email copywriting instructions clearly and cleanly for AI agents. Please only return a structure instructions and nothing else."
# contexts_contradictions = """Look at these sets of instructions and first help me extract rules that have contradictions in this format.\n\n
# <rule>\n
# <Contradicting role>\n\n
# <rule>\n
# <Contradicting role>\n\n
# """

contexts= """
You are an expert at creating well structure prompt for AI Agents that will be working for Salaria. Look at these
instructions and use them to create a well structure prompt with the following patterns. Make sure the email format remains
exact as the one in the instructions:\n\n
<Rationale>\n
<Goal>\n
<Agent Role>\n
<Task>\n
<Rules>\n\n
"""

# contexts_faq= """
# I need you to take this faq information and about my organization document and then streamline it as much relevant info
# as possible that can serve as an "About My company" document for Salaria Sales Solutions's top-of-funnel sales activities.
# """


def structure_instruction(instructions):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": f"{contexts}"},
            {"role": "user", "content": instructions}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content


if __name__ == '__main__':
    my_email = """
    Hi Adam

We saw your Sales Account Executive role on LinkedIn at Kersheh Group and thought you might like that we can manage prospecting, cold calling and setting meetings across sleepwear channels so your team stays focused on closing national chain deals and executing account plans while cutting costs.

We provide prospecting and cold calling services with sleepwear account experience and North America wholesale chain outreach. We can set qualified meetings and manage incremental revenue campaigns so your team can focus on closing national chain deals on a lean cost model.

As the Vice President of Sales you’re positioned to steer pipeline growth. I also sent a note to Bob Alen in case this is relevant to marketing. Our contracts are month to month with no commitment and we can work alongside existing agencies or internal teams.

Can we set up a call to introduce ourselves?
    """
    subject_line = generate_email_subject(email=my_email)
    print(subject_line)