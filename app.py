import os
import streamlit as st
import google.generativeai as genai
import json
import re

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="Deadline Dodger",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING (Senior UX Design) ---
st.success("Study roadmap generated!")
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007BFF;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stTextArea textarea { background-color: #161B22; color: #E6EDF3; }
    .success-text { color: #238636; font-weight: bold; }
    .warning-text { color: #D29922; }
    .header-gradient {
        background: -webkit-linear-gradient(#00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND LOGIC ---
class CramEngine:
    def __init__(self, api_key):
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def call_ai(self, prompt):
        try:
            if not self.model:
                return "Error: Please provide a valid Gemini API Key in the sidebar."
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI Error: {str(e)}"

# --- APP INITIALIZATION ---
st.sidebar.title("🛠️📚 Deadline Dodger ")
st.sidebar.markdown("""
### About

Built for **Vibe2Ship Hackathon 2026**

**Powered by**
- Google Gemini
- Python
- Streamlit

💡 Enter your Gemini API key below to use the app.
""")
api_key = st.sidebar.text_input(...)
api_key = os.getenv("GOOGLE_API_KEY")
engine = CramEngine(api_key)

st.markdown('<h1 class="header-gradient">📚 Deadline Dodger</h1>', unsafe_allow_html=True)
st.markdown(
    "### *Beat your deadlines with AI-powered study plans, revision notes, and quizzes.* 🚀"
)

# --- SESSION STATE MGMT ---
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False

# --- TABS INTERFACE ---
tab1, tab2, tab3 = st.tabs(["🕒 Cram Schedule", "📝 Cheat-Sheet", "🧠 Mock Examiner"])

# --- FEATURE 1: CRAM SCHEDULE ---
with tab1:
    st.header("1. Priority Action Plan")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        time_left = st.number_input("Hours until deadline:", min_value=1, max_value=72, value=5)
        subject = st.text_input("Subject/Topic:", placeholder="e.g., Organic Chemistry")
        btn_schedule = st.button("🚀 Generate Study Roadmap")
    
    with col2:
        syllabus = st.text_area("Paste your syllabus, lecture notes, assignment details, or project brief here...")
        
    if btn_schedule:
        with st.spinner("🤖 Gemini is creating your personalized study roadmap..."):
            prompt = f"""
            Act as a high-performance productivity coach. I have an exam/submission in {time_left} hours.
            Subject: {subject}
            Syllabus: {syllabus}
            Create a strict, hour-by-hour action plan. Include 5-minute 'sanity breaks'. 
            Focus ONLY on high-yield topics that provide 80% of results. 
            Format as a clear Markdown table.
            """
            result = engine.call_ai(prompt)
            st.markdown(result)

# --- FEATURE 2: CHEAT-SHEET ---
with tab2:
    st.header("2. Instant Cheat-Sheet")
    content = st.text_area("Input Study Material:", height=250, key="cs_input", placeholder="Paste your study material here...")
    
    if st.button("📝 Generate Cheat Sheet"):
        if content:
            with st.spinner("📝 Creating your revision cheat sheet..."):
                prompt = f"""
                Convert the following text into a 'last-minute' cheat sheet:
                {content}
                Rules:
                - Use bold for key terms.
                - Use bullet points for micro-notes.
                - Create a section for 'Core Formulas' or 'Definitions'.
                - Maximum density, zero fluff.
                """
                result = engine.call_ai(prompt)
                st.info("💡 Tip: Screenshot this for your phone lockscreen!")
                st.markdown(result)
        else:
            st.warning("Please paste some content first.")

# --- FEATURE 3: MOCK EXAMINER ---
with tab3:
    st.header("3. AI Mock Examiner")
    quiz_topic = st.text_input("Quiz Topic:", placeholder="Enter the topic you want to practice")
    
    if st.button("🧠 Generate Mock Quiz"):
        with st.spinner("🧠 Preparing your mock exam..."):
            prompt = f"""
            Generate a 5-question multiple choice quiz on {quiz_topic}.
            Format the response strictly as a JSON list of objects like this:
            [
              {{"question": "...", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "..."}}
            ]
            Keep it challenging but fair.
            """
            raw_quiz = engine.call_ai(prompt)
            # Basic JSON extraction logic
            try:
                # Clean the response in case AI adds markdown code blocks
                clean_json = re.search(r'\[.*\]', raw_quiz, re.DOTALL).group()
                st.session_state.quiz_data = json.loads(clean_json)
                st.session_state.quiz_submitted = False
            except:
                st.error("Failed to parse quiz. Try clicking again.")

    if st.session_state.quiz_data:
        user_answers = []
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                choice = st.radio(f"Select answer for Q{i+1}", q['options'], key=f"q_{i}")
                user_answers.append(choice)
            
            submitted = st.form_submit_button("Grade Me")
            if submitted:
                st.session_state.quiz_submitted = True
        
        if st.session_state.quiz_submitted:
            score = 0
            for i, q in enumerate(st.session_state.quiz_data):
                if user_answers[i] == q['answer']:
                    score += 1
                    st.success(f"Q{i+1}: Correct!")
                else:
                    st.error(f"Q{i+1}: Incorrect. The answer is {q['answer']}")
                st.caption(f"Reasoning: {q['explanation']}")
            
            st.metric("Final Score", f"{score}/5")
            if score == 5:
                st.balloons()

# --- FOOTER ---
st.markdown("---")
st.caption("Deadline Dodger | Built for the Hackathon |  Made with ❤️ for Vibe2Ship Hackathon")

