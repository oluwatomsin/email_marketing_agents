from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# contexts = "You are a helpful assistant that structures email copywriting instructions clearly and cleanly for AI agents. Please only return a structure instructions and nothing else."
contexts_contradictions = """Look at these sets of instructions and first help me extract rules that have contradictions in this format.\n\n
<rule>\n
<Contradicting role>\n\n
<rule>\n
<Contradicting role>\n\n
"""

# contexts= """
# You are an expert at creating well structure prompt for AI Agents that will be working for Salaria. Look at these
# instructions and use them to create a well structure prompt with the following patterns:\n
# <Rationale>\n
# <Goal>\n
# <Agent Role>\n
# <Task>
# <Rules>
# """

contexts_faq= """
I need you to take this faq information and about my organization document and then streamline it as much relevant info 
as possible that can serve as an "About My company" document for Salaria Sales Solutions's top-of-funnel sales activities.
"""


def structure_instruction(instructions):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": f"{contexts_contradictions}"},
            {"role": "user", "content": instructions}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content


if __name__ == '__main__':
    instructions = """
    Help me build the third paragraph of an email for my company, salaria sales solutions (salariasales.com). With this 
    strategy which we call the SDR recruitment strategy, we are targeting companies that are hiring for sales development 
    or business development representatives - BDRs or SDR positions - which is a junior sales position that is focused on 
    top of the funnel sales tasks - the exact same tasks that salaria specializes in. This is different from our AE 
    strategy, where we are targeting companies that are hiring for AE positions. With that strategy, we are making an 
    argument to companies that they should hire us to help support their sales reps - so instead of their sales reps 
    doing all of the full sales cycle of activities themselves, including top of the funnel sales tasks, we can take 
    care of those tasks for their sales reps and their sales reps can be more focused on revenue generating activities. 
    With the SDR Strategy, We look for companies with open SDR job posts and send them outreach to introduce ourselves 
    as an alternative to hiring internally. We also work with companies that have internal teams, we usually will augment
    existing SDR teams. I want you to help me build the first paragraph of the email. The first paragraph has to mention 
    the job post, the website we found it on and mention the company’s name. Then we immediately have to tie in the idea
    that we can take on many of the same sales tasks that are listed on the job description. I want you to pull information
    directly from their job description to customize the first paragraph. I want you to use specific words and phrases 
    from the job description in this paragraph. I want you to try to identify their target audience or their customer 
    audience or ideal customer industry from the job description that I feed you as well as the company information that
    I feed you from their website and Linkedin. I want you to craft an ultra-customized first paragraph using all of the
    information I feed you. I want you to tie in many of the things that they are looking for with the services that we 
    provide. The second paragraph of the email, is more focused on salaria, explicitly listing the services that we 
    provide and then continues to make the argument that we can take on sales development, SDR, top-of-the-funnel sales 
    tasks that are listed in the job post. You don’t want to sound too repetitive with paragraph one where we also pull 
    tasks from the job post and say we can help take on those tasks. I’m going to give you the first paragraph of this 
    email so that you can read how it starts off so that you can make sure it flows together.  I want you to craft an 
    ultra-customized second paragraph using all of the information I feed you. The third paragraph, the paragraph we are
    creating here, is focused on the actual person we are reaching out to, the lead, the contact. We are trying to speak
    to them and their job responsibility. In the third paragraph, we are trying to tie in how we are reaching out to 
    them specifically, because we think they are the right person to reach out to. Additionally, we want to tell the 
    lead that we also reached out to their colleague. I’m going to give you the other person’s information and I want 
    you to mention that we also reached out to them not knowing who this might fall under. Sometimes we work with the 
    marketing team, other times our main POC is in sales. We also sometimes reach out to their CEO or the head of the 
    company as we know we will have to get their buy-in and sometimes a disruptive model requires the attention of the 
    CEO. But I always want to admit that they likely drive all sales and marketing decisions (depending on which lead we
    are reaching out to. So make sure to show respect for the lead we are messaging. I’m now going to copy and paste the
    entire homepage of salaria as well as some FAQs for you to learn about us. I’m also going to copy and paste our 
    current email template for you to understand the argument we are making to sales leads currently and see how we 
    currently write paragraph three. Be sure to tie in specific information from the lead’s linkedin and their job 
    information into this paragraph.  
    
    Instruction 2: 
    
    I’m now going to copy and paste all the first and second paragraphs of the email that you wrote in a separate chat, 
    the information from the company website, and the job description, the names and titles of the other people we are 
    reaching out to
    
    Follow the Rules for paragraph 3: 
    
    1. This paragraph is supposed to tie in the lead’s position and their background and experience with why we reached 
    out to them specifically
    2. I’m going to feed you information about the lead from their linkedin including their title, job description and 
    about us. I’m also going to feed you the job post and about info on the company again. Craft a paragraph that starts
    with us mentioning their title and then explaining why we reached out to them. Use specific language (words, phrases)
    from their title. 
    3. If I am unable to find information about them and their position on their linkedin, I will at least have their 
    title. Make an argument specific to their title and what you know about the job responsibilities of a person with 
    their job title - and again tie in why we think they specifically would be interested in our services given their 
    position 
    4. If the lead is the head of the company (CEO, president, chairman, founder) then I want you to address them as the
    head of the company. Its weird when you say “I saw that you are the CEO and thought you might be interested..” that 
    just sounds silly - the CEO is unusually interested in every component of the company - noticing their title as CEO 
    made you think they might be interested in Salaria? You see how that just sounds silly? Usually when its the head of
    the company, I make the argument that we are reaching out to them specifically because our model and our services 
    are so disruptive and touch every corner of the business - we usually need the buy in of the head of the company to 
    push through something as unique, different and disruptive as our model for lead generation
    5. In this paragraph, you also have to emphasize that we offer month to month contracts with no commitment - so they
    can just try us out to see if we are can fit in - you have to always mention this - this is a requirement
    6. Additionally, you have to mention that even if they are already working with another agency or have an internal 
    team, we’d like the chance to just introduce ourselves and share our very unique model - you have to always mention 
    this - this is a requirement
    7. No more than 300 characters
    8. Do not start the paragraph with the lead’s name
    9. When I tell you that I reached out to their CEO, make sure to be respectful of the actual we are emailing. So for
    example, if we are reaching out to the head of sales, I think we should say, you “I sent a quick note to [CEO], since
    this likely ties into broader growth goals—but I know you’re the one leading the charge on sales execution.” If I 
    reached out to both their CEO and their other colleague in sales or marketing, I would want to say something like 
    “I also sent a quick note to [CEO] and [Head of Marketing], since what we do tends to touch all three fronts—sales 
    execution, marketing alignment, and overall growth. That said, I know you’re leading the charge on the sales side, 
    so I wanted to make sure this was on your radar too.” I’m reaching out to the head of the company or CEO, make sure 
    to say something like “I sent a quick note to [head of marketing name] and [head of sales name] as I’m sure they 
    drive sales and marketing but I wanted to touch base with you to ensure this aligns with your growth goals
    10. Do not use special characters from the info I give you 
    11. When referencing someone else that we reached out to, always use their full name, first and last name
    12. Never referred to a company’s founding year, thats cheesy sales 
    13. If I don’t explicitly mention that we are contacting someone like the CEO, don’t mention that we are reaching 
    out to the CEO. You should only reference people if I’m explicitly telling you that we are contacting them as well. 
    14. Don’t say something is “worth a look” or suggesting they would be dumb to not try us. You also should be more 
    explicitly clear that our contracts are month to month and non committal. I think you should also be more clear that
    if they are using another agency or have an internal team, we’d love to introduce our unique model. But there is a 
    better way to say it than “worth a look or worth a shot” 
    15.you overuse the super long dash People are now calling it the chatgpt dash as it gives away the fact that we used
    chatgpt. Don't use it anymore. Use a normal dash or no dash at all or re-write it differently. This is the dash I’m 
    referring to: ( — ) — — this dash gives it away that I’m using ai like chatgpt. As you write this, please don’t 
    include any dashes (—). You can use more commas or write it differently to not need dashes.
    16. Always end the email with a direct CTA. Can we set up a call to introduce ourselves? Make sure you separate it 
    from the final paragraph. The CTA should be it’s standalone sentence at the bottom separated from the last paragraph
    always.
    17. Make sure you use the first and last name of the other lead’s we are saying that we are reaching out to - use 
    their full name, not just their first name
    18. Never mention the mission statement of a lead’s company - that is a very cheesy sales technique and perceived as
    a lazy way to personalize. If you talk about how much you “appreciate” someones values and mission statements, they 
    might perceive that as disingenuous and overly salesy
    19. Never mention the name Salaria in the email - never mention Salaria by name - always say “We” like “We can help 
    you with..”
    20. Start the email off with "Hi Lead First Name" - fill in the first name field with the first name of the person 
    I’m messaging
    21. Sometimes job titles on job posts are irregular with odd niche subtitles, etc. Such as Sales Development 
    Representative (Full-Time). In that example, full time should not be included in the email, it should just be Sales 
    Development Representative. Make sure to standardize all titles and take any irregularities found in the job title 
    on the job post, such as regional references, specializations, etc. 
    22. To inform you on who we are emailing and who else we are contacting to create this paragraph, we are going to 
    label the person for this email as contact 1, then contact 2, then contact 3. We are going to start with crafting 
    paragraph 3 for contact 1, then we are going to create it for contact 2, and then 3. Just know that each person will
    be labeled as such 
    23. When address someone’s title and responsibilities don’t make statements as if we know exactly what their 
    responsibilities are like “you are clearly driving sales execution” or “you are obviously the right person for this”
    ...never make definitive statements like that as you dont know for sure what someone does and if they are involved 
    in this 
    24. Only reference the contacts or people I say that we are reaching out to and labeling contact 1,2, 3 - dont add 
    anyone else onto the paragraph that I dont explicitly reference 
    25. To be clear, The format of the third paragraph should be “As the [title], [generic reason for them being the 
    right person to reach out to for lead generation]. I also sent a note to [contact 2] and [contact 3] in case this 
    [generic reason for why this might be relevant to them]. 
    26. Don’t pull too much information out of their linkedin to customize this paragraph. I think if you over customize
    this paragraph, the lead will be able to tell when you are being disingenuous. The lead will know you are just 
    pulling keywords from their titles. 
    """
    output = structure_instruction(instructions)
    print(output)
