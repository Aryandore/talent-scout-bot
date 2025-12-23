# 🤖 TalentScout - AI Hiring Assistant

**TalentScout** is an intelligent, AI-powered recruitment chatbot designed to streamline the initial candidate screening process. Built with **Streamlit** and **Llama 3 (via Groq)**, it features resume parsing, automated information extraction, and dynamic technical question generation.

## 🌟 Features

* **📄 Resume Parsing:** Users can upload a PDF resume. The system uses `pypdf` to extract text and AI to intelligently parse unstructured data into structured JSON (Name, Email, Tech Stack).
* **🧠 Context-Aware AI:** Powered by **Llama 3.3**, the bot understands context and maintains a professional "Recruiter" persona.
* **❓ Dynamic Question Generation:** Automatically generates 3 challenging, role-specific technical questions based on the candidate's declared tech stack.
* **💬 Interactive Interview:** Conducts a one-on-one interview, asking questions sequentially and waiting for user responses before proceeding.
* **📊 Session Management:** Robust use of `st.session_state` to ensure data persists across UI re-runs.

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Python)
* **LLM Engine:** Llama 3.3-70b-versatile (via [Groq API](https://groq.com/))
* **PDF Processing:** `pypdf`
* **Environment Management:** `python-dotenv`

## 📂 Project Structure

```text
TalentScout_Bot/
├── .env                  # API Keys (Not shared in repo)
├── requirements.txt      # Project dependencies
├── app.py                # Main application logic (UI & State Management)
├── prompts.py            # AI System Prompts & Logic
└── README.md             # Documentation