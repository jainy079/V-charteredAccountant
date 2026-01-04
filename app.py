import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import pandas as pd
import plotly.express as px
import datetime

# ==========================================
# 👇 SETUP & CONFIGURATION 👇
# ==========================================
GOOGLE_API_KEY = "AIzaSyCwjIu4Hc4HczJUeZdfVgw1j1VxWPZq-JM"  # Apni Key check kar lena
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(
    page_title="V-Chartered Pro",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (PROFESSIONAL THEME) ---
st.markdown("""
<style>
    /* Global Font & Colors */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }
    
    /* Splash Screen Styling */
    .splash-text {
        font-size: 50px;
        font-weight: bold;
        color: #004B87;
        text-align: center;
        animation: fadeIn 2s;
    }
    
    /* Professional ICAI Blue Theme */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #003366;
        color: white;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #004B87;
        color: white;
        border-radius: 5px;
        height: 3em;
        width: 100%;
    }
    
    /* Cards */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    /* Kuchu Assistant Box */
    .kuchu-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 👇 STATE MANAGEMENT (Login & Timer) 👇
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'splash_shown' not in st.session_state:
    st.session_state['splash_shown'] = False

# ==========================================
# 1️⃣ SPLASH SCREEN (Animated Entry)
# ==========================================
if not st.session_state['splash_shown']:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<p class="splash-text">V-Chartered</p>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;">The Ultimate CA AI Companion</p>', unsafe_allow_html=True)
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02) # Animation speed
            bar.progress(i + 1)
        time.sleep(0.5)
    placeholder.empty()
    st.session_state['splash_shown'] = True

# ==========================================
# 2️⃣ LOGIN SYSTEM
# ==========================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Professional Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login to Dashboard")
            
            if submitted:
                # Demo login logic (Real mein Database use hota hai)
                if username.lower() == "vanshika" and password == "ca2026":
                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = "Vanshika Agrawal"
                    st.success("Access Granted! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid Credentials! (Try: vanshika / ca2026)")
    st.stop() # Stop app here if not logged in

# ==========================================
# 3️⃣ MAIN DASHBOARD
# ==========================================

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title(f"Welcome, {st.session_state['user_name'].split()[0]}")
    st.markdown("---")
    menu = st.radio("Navigation", ["📊 Performance Analytics", "📝 Exam Mode (Timer)", "🔍 Kuchu Answer Checker"])
    st.markdown("---")
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- TAB 1: ANALYTICS (DASHBOARD) ---
if menu == "📊 Performance Analytics":
    st.title("📈 Performance Dashboard")
    st.markdown("Analytics based on your recent activity.")
    
    # Fake Data for Visualization (Baad mein Real connect kar sakte hain)
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="metric-card"><h3>📚 Subjects Covered</h3><h1>4/8</h1></div>', unsafe_allow_html=True)
    c2.markdown('<div class="metric-card"><h3>✅ Accuracy Rate</h3><h1>78%</h1></div>', unsafe_allow_html=True)
    c3.markdown('<div class="metric-card"><h3>⏳ Study Hours</h3><h1>12 hrs</h1></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Graph using Plotly
    data = {'Subject': ['Audit', 'SFM', 'FR', 'Law', 'DT'], 'Score': [65, 80, 45, 70, 55]}
    df = pd.DataFrame(data)
    fig = px.bar(df, x='Subject', y='Score', color='Score', title="Subject-wise Strength Analysis")
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 **Kuchu's Insight:** FR (Financial Reporting) needs more attention. Your SFM is strong!")

# --- TAB 2: EXAM MODE (TIMER & PATTERN) ---
elif menu == "📝 Exam Mode (Timer)":
    st.title("🎓 Real Exam Simulator")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        subject = st.selectbox("Select Subject", ["Audit", "Financial Reporting", "SFM", "Direct Tax", "IDT", "Law"])
        level = st.selectbox("Exam Level", ["CA Final", "CA Inter"])
        q_type = st.selectbox("Question Type", ["Case Study Based (5 Marks)", "Descriptive (14 Marks)", "MCQ Scenario (2 Marks)"])
    
    with col2:
        st.markdown("### ⏱️ Timer")
        exam_time = st.number_input("Minutes", 5, 180, 15)
        if st.button("Start Exam"):
            st.session_state['exam_active'] = True
            st.session_state['start_time'] = time.time()

    if st.button("📄 Generate Question Paper"):
        with st.spinner("Generating ICAI Level Question..."):
            prompt = f"""
            Create a TOUGH {level} level question for {subject}.
            Type: {q_type}.
            
            Strictly follow ICAI Exam Pattern.
            If 'Case Study', provide a long scenario first, then the question.
            Do NOT provide the answer yet.
            """
            response = model.generate_content(prompt)
            st.session_state['current_question'] = response.text
            
    if 'current_question' in st.session_state:
        st.markdown("---")
        st.markdown("### 📝 Question Paper")
        st.markdown(st.session_state['current_question'])
        
        st.markdown("---")
        user_ans = st.text_area("Type your answer here (Simulate Exam):", height=200)
        
        if st.button("Submit & Evaluate"):
            with st.spinner("Kuchu is checking your paper..."):
                eval_prompt = f"""
                Act as a Strict ICAI Examiner.
                Question: {st.session_state['current_question']}
                User Answer: {user_ans}
                
                Evaluate strictly on Key Provisions, Keywords, and Conclusion.
                Give Marks out of total.
                Give Remarks as 'Kuchu Assistant'.
                """
                eval_res = model.generate_content(eval_prompt)
                
                st.markdown('<div class="kuchu-box">', unsafe_allow_html=True)
                st.markdown(f"🤖 **Kuchu's Remarks:**\n\n{eval_res.text}")
                st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: KUCHU ANSWER CHECKER (UPLOAD) ---
elif menu == "🔍 Kuchu Answer Checker":
    st.title("🔍 Kuchu Assistant (Scanner)")
    st.write("Upload handwritten notes. Kuchu will check them.")
    
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Sheet", width=400)
        
        if st.button("Check Now"):
            with st.spinner("Kuchu is analyzing handwriting..."):
                prompt = """
                You are 'Kuchu', a friendly but strict CA Assistant.
                Check this answer sheet.
                1. Identify Topic.
                2. Point out missing ICAI Keywords.
                3. Give marks.
                4. End with a motivating quote for Vanshika.
                """
                response = model.generate_content([prompt, image])
                
                st.markdown('<div class="kuchu-box">', unsafe_allow_html=True)
                st.markdown(f"🤖 **Kuchu Says:**\n\n{response.text}")
                st.markdown('</div>', unsafe_allow_html=True)
