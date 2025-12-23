import streamlit as st
import os
import json
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
import prompts  # Importing our updated prompts

# 1. SETUP
load_dotenv()
st.set_page_config(page_title="TalentScout AI", page_icon="🤖")

try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except:
    st.error("Please set your GROQ_API_KEY in .env")
    st.stop()

MODEL_NAME = "llama-3.3-70b-versatile" # Updated model name

# 2. HELPER FUNCTIONS
def extract_text_from_pdf(uploaded_file):
    pdf = PdfReader(uploaded_file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

def get_ai_response(messages, json_mode=False):
    """
    Helper to get response from Groq. 
    json_mode=True forces the model to return valid JSON (great for extraction).
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3 if json_mode else 0.7,
            response_format={"type": "json_object"} if json_mode else {"type": "text"}
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# 3. SESSION STATE INITIALIZATION
if "stage" not in st.session_state:
    st.session_state.stage = "UPLOAD"  # Stages: UPLOAD, CONFIRM_INFO, INTERVIEW, FEEDBACK
if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {}
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 4. UI LOGIC

st.title("🤖 TalentScout Hiring Assistant")

# --- STAGE 1: UPLOAD RESUME ---
if st.session_state.stage == "UPLOAD":
    st.write("### 👋 Welcome! Please upload your resume to begin.")
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("Analyzing your resume..."):
            # A. Extract Text
            resume_text = extract_text_from_pdf(uploaded_file)
            
            # Check if PDF reading failed
            if not resume_text.strip():
                st.error("This PDF seems to be an image or empty. Please upload a text-based PDF.")
                st.stop()

            # B. AI Extraction
            extract_prompt = prompts.RESUME_ANALYSIS_PROMPT.format(resume_text=resume_text)
            messages = [{"role": "user", "content": extract_prompt}]
            
            raw_json = get_ai_response(messages, json_mode=True)
            
            # --- FIX: CLEAN THE JSON STRING ---
            # Llama 3 often adds ```json at the start. We remove it.
            clean_json = raw_json.replace("```json", "").replace("```", "").strip()
            
            try:
                # Parse JSON safely
                candidate_data = json.loads(clean_json)
                st.session_state.candidate_info = candidate_data
                st.session_state.stage = "CONFIRM_INFO"
                st.rerun()
            except Exception as e:
                st.error("Could not read resume automatically. Please try again.")
                # SENIOR DEBUGGING: Show exactly what failed so you can fix it
                with st.expander("See Error Details (For Debugging)"):
                    st.write(f"Error: {e}")
                    st.write("AI Raw Response:")
                    st.code(raw_json)

# --- STAGE 2: CONFIRM INFO ---
elif st.session_state.stage == "CONFIRM_INFO":
    st.write("### 📋 Is this information correct?")
    
    # Editable form in case AI made a mistake
    with st.form("info_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full Name", st.session_state.candidate_info.get("full_name"))
        email = col2.text_input("Email", st.session_state.candidate_info.get("email"))
        tech_stack = st.text_area("Tech Stack", str(st.session_state.candidate_info.get("tech_stack")))
        
        submitted = st.form_submit_button("Yes, Start Interview")
        
        if submitted:
            # Generate Questions silently in background
            with st.spinner("Generating Technical Questions..."):
                q_prompt = prompts.QUESTION_GENERATION_PROMPT.format(tech_stack=tech_stack)
                # We ask for a JSON list specifically
                messages = [
                    {"role": "system", "content": "You return strictly a JSON object with a key 'questions' containing a list of 3 strings."},
                    {"role": "user", "content": q_prompt}
                ]
                q_response = get_ai_response(messages, json_mode=True)
                
                try:
                    q_json = json.loads(q_response)
                    st.session_state.questions = q_json["questions"]
                    st.session_state.stage = "INTERVIEW"
                    
                    # Add first question to chat
                    first_q = st.session_state.questions[0]
                    st.session_state.chat_history.append({"role": "assistant", "content": f"Great! Let's start. \n\n**Question 1:** {first_q}"})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating questions: {e}")

# --- STAGE 3: INTERVIEW (ONE BY ONE) ---
elif st.session_state.stage == "INTERVIEW":
    
    # Display Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Chat Input
    if user_ans := st.chat_input("Your answer..."):
        # 1. Show User Answer
        st.session_state.chat_history.append({"role": "user", "content": user_ans})
        with st.chat_message("user"):
            st.markdown(user_ans)
        
        # 2. Logic: Move to next question or Finish
        st.session_state.current_q_index += 1
        
        if st.session_state.current_q_index < len(st.session_state.questions):
            # Ask Next Question
            next_q = st.session_state.questions[st.session_state.current_q_index]
            bot_msg = f"**Question {st.session_state.current_q_index + 1}:** {next_q}"
            
            st.session_state.chat_history.append({"role": "assistant", "content": bot_msg})
            with st.chat_message("assistant"):
                st.markdown(bot_msg)
        else:
            # Interview Finished
            finish_msg = "Thank you! You've answered all questions. Our engineering team will review your responses and get back to you."
            st.session_state.chat_history.append({"role": "assistant", "content": finish_msg})
            with st.chat_message("assistant"):
                st.markdown(finish_msg)
            
            # Optional: Move to End State to prevent more typing
            st.session_state.stage = "END"
            st.rerun()

# --- STAGE 4: END ---
elif st.session_state.stage == "END":
    st.balloons()
    st.success("Interview Submitted Successfully!")
    st.write("Your responses have been recorded.")
    
    if st.button("Start New Candidate"):
        st.session_state.clear()
        st.rerun()