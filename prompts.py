# prompts.py

# 1. System Prompt for the Chat Persona
SYSTEM_PROMPT = """
You are "TalentScout," a friendly and professional technical recruiter. 
Your goal is to assess the candidate's declared tech stack. 
Keep your responses concise and professional.
"""

# 2. Prompt to extract data from Resume Text
RESUME_ANALYSIS_PROMPT = """
Analyze the following resume text and extract the candidate's information in strictly valid JSON format.
Keys required: "full_name", "email", "years_of_experience", "tech_stack" (as a list of strings).
Do not add any conversational text, just the JSON.

Resume Text:
{resume_text}
"""

# 3. Prompt to generate technical questions
QUESTION_GENERATION_PROMPT = """
Based on the candidate's tech stack: {tech_stack}, generate exactly 5 simple to hard technical interview questions.
Return them as a Python list of strings. Do not number them. 
Example format: ["Question 1 content", "Question 2 content", "Question 3 content"]
"""