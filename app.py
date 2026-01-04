import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import sqlite3
import hashlib
import pandas as pd
import datetime
import base64

# ==========================================
# 🛡️ SECURE API KEY
# ==========================================
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        st.error("🚨 API Key Missing in Secrets!")
        st.stop()
except Exception as e:
    st.error(f"Setup Error: {e}")

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="V-Chartered Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SUBJECT LISTS ---
CA_FINAL_SUBJECTS = ["Financial Reporting (FR)", "Advanced Financial Management (AFM)", "Advanced Auditing", "Direct Tax", "Indirect Tax (GST)", "IBS"]
CA_INTER_SUBJECTS = ["Advanced Accounting", "Corporate Laws", "Taxation", "Costing", "Auditing", "FM-SM"]

# ==========================================
# 🎨 DYNAMIC THEME CSS (Smart Colors)
# ==========================================
if 'theme' not in st.session_state: st.session_state['theme'] = 'light'

if st.session_state['theme'] == 'dark':
    bg_color = "#0E1117"
    card_bg = "#1E1E1E"
    text_color = "white"
    title_color = "#90CAF9"
    border_color = "#333"
else:
    bg_color = "#F0F4F8"
    card_bg = "white"
    text_color = "#0d1b2a"
    title_color = "#004B87"
    border_color = "#E1E8ED"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; }}
    h1, h2, h3, h4, h5, p, span, div, label, li {{ color: {text_color} !important; }}
    
    .feature-card {{
        background-color: {card_bg}; padding: 25px; border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1); text-align: center;
        border: 1px solid {border_color}; margin-bottom: 20px; transition: transform 0.2s;
    }}
    .feature-card:hover {{ transform: translateY(-5px); border-color: {title_color}; }}
    .feature-card h3 {{ color: {title_color} !important; }}
    
    .stButton>button {{ 
        background-color: #004B87 !important; color: white !important; 
        border-radius: 8px; font-weight: 600; width: 100%; border: none; padding: 12px; 
    }}
    .stTextInput input, .stSelectbox div, .stTextArea textarea {{ color: {text_color} !important; }}
    .splash-title {{ font-size: 60px; color: {title_color} !important; text-align: center; font-weight: bold; }}
    
    /* Back Button Style */
    div.stButton > button:first-child {{
        background-color: #004B87; color: white;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 💾 DATABASE FUNCTIONS
# ==========================================
def init_db():
    conn = sqlite3.connect('vchartered_db.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS results (email TEXT, subject TEXT, score INTEGER, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs (email TEXT, action TEXT, details TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def log_activity(email, action, details=""):
    try:
        conn = sqlite3.connect('vchartered_db.db')
        c = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO activity_logs VALUES (?, ?, ?, ?)", (email, action, details, timestamp))
        conn.commit()
        conn.close()
    except: pass

def create_user(email, username, password):
    conn = sqlite3.connect('vchartered_db.db')
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (email, username, hashed_pw))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def check_login(email, password):
    conn = sqlite3.connect('vchartered_db.db')
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT username FROM users WHERE email=? AND password=?", (email, hashed_pw))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_name(email):
    conn = sqlite3.connect('vchartered_db.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE email=?", (email,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else "Student"

def get_leaderboard():
    conn = sqlite3.connect('vchartered_db.db')
    df = pd.read_sql_query("SELECT email, subject, score FROM results ORDER BY score DESC LIMIT 5", conn)
    conn.close()
    return df

def get_logs():
    conn = sqlite3.connect('vchartered_db.db')
    df = pd.read_sql_query("SELECT * FROM activity_logs ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def save_score(email, subject, score):
    conn = sqlite3.connect('vchartered_db.db')
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT INTO results VALUES (?, ?, ?, ?)", (email, subject, score, date))
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 🚀 SMART NAVIGATION (BACK BUTTON FIX)
# ==========================================
# Ye function Login ID ko URL mein chipka ke rakhta hai
def navigate_to(page_name):
    current_uid = st.query_params.get("uid", None)
    params = {"page": page_name}
    if current_uid:
        params["uid"] = current_uid # Login ID mat khona
    st.query_params.update(params)
    time.sleep(0.1)
    st.rerun()

# Get Current Page from URL
url_page = st.query_params.get("page", "Home")
st.session_state['current_page'] = url_page

# ==========================================
# ✨ SPLASH SCREEN
# ==========================================
if 'splash_shown' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(f"<br><br><br><div class='splash-title'>V-Chartered</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:grey;'>Made by Atishay Jain & Google Gemini</p>", unsafe_allow_html=True)
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            bar.progress(i + 1)
        time.sleep(0.5)
    placeholder.empty()
    st.session_state['splash_shown'] = True

# ==========================================
# 🔐 AUTH SYSTEM (PERSISTENT)
# ==========================================
if 'user_email' not in st.session_state: st.session_state['user_email'] = None
if 'user_name' not in st.session_state: st.session_state['user_name'] = None

# 1. URL Check (Auto-Login Logic)
query_params = st.query_params
if "uid" in query_params:
    try:
        decoded_email = base64.b64decode(query_params["uid"]).decode('utf-8')
        if st.session_state['user_email'] != decoded_email:
            st.session_state['user_email'] = decoded_email
            st.session_state['user_name'] = get_user_name(decoded_email)
            st.rerun()
    except: pass

# 2. LOGIN PAGE (Forms for Browser Save)
if not st.session_state['user_email']:
    st.markdown("<br><br><div class='splash-title'>V-Chartered</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            st.info("Browser 'Save Password' puchega toh YES karna!")
            # 👇 Is Form ki wajah se Chrome password save karega
            with st.form("login_form"):
                email = st.text_input("Email ID")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login & Save")
                
                if submit:
                    user = check_login(email, password)
                    if user:
                        encoded_email = base64.b64encode(email.encode()).decode()
                        # Update URL to keep logged in
                        st.query_params["uid"] = encoded_email
                        st.query_params["page"] = "Home"
                        
                        st.session_state['user_email'] = email
                        st.session_state['user_name'] = user
                        log_activity(email, "Login", "Success")
                        st.rerun()
                    else: st.error("Wrong Credentials")
        
        with tab2:
            new_email = st.text_input("New Email")
            new_name = st.text_input("Full Name")
            new_pass = st.text_input("New Password", type="password")
            if st.button("Create Account"):
                if create_user(new_email, new_name, new_pass): 
                    st.success("Account Created! Login Now.")
                else: st.error("Email Taken")
    st.stop()

# ==========================================
# 🕵️‍♂️ SIDEBAR
# ==========================================
IS_ADMIN = "admin" in st.session_state['user_email'].lower() or "atishay" in st.session_state['user_email'].lower()

with st.sidebar:
    st.title(f"👤 {st.session_state['user_name']}")
    
    if st.button("🌗 Change Theme"):
        st.session_state['theme'] = 'dark' if st.session_state['theme'] == 'light' else 'light'
        st.rerun()
    
    if st.button("Logout"):
        log_activity(st.session_state['user_email'], "Logout", "Clicked")
        st.query_params.clear()
        st.session_state['user_email'] = None
        st.rerun()

    if IS_ADMIN:
        st.markdown("---")
        if st.button("🕵️‍♂️ Admin Panel"): navigate_to("Admin")
        
    st.markdown("---")
    st.markdown("### 🏆 Leaderboard")
    lb = get_leaderboard()
    if not lb.empty:
        for i, row in lb.iterrows():
            st.markdown(f"🥇 **{row['score']}** - {row['email'].split('@')[0]}")
    
    if st.button("🏠 Home"): navigate_to("Home")

# ==========================================
# 🏠 HOME PAGE
# ==========================================
if st.session_state['current_page'] == "Home":
    st.title("Dashboard")
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    
    with c1:
        st.markdown('<div class="feature-card"><h3>📑 Mock Test</h3></div>', unsafe_allow_html=True)
        if st.button("Start Test"): 
            log_activity(st.session_state['user_email'], "Visit", "Test")
            navigate_to("Test")
    with c2:
        st.markdown('<div class="feature-card"><h3>📸 Checker</h3></div>', unsafe_allow_html=True)
        if st.button("Open Scanner"): 
            log_activity(st.session_state['user_email'], "Visit", "Checker")
            navigate_to("Checker")
    with c3:
        st.markdown('<div class="feature-card"><h3>🤖 Kuchu</h3></div>', unsafe_allow_html=True)
        if st.button("Chat"): 
            log_activity(st.session_state['user_email'], "Visit", "Kuchu")
            navigate_to("Kuchu")
    with c4:
        st.markdown('<div class="feature-card"><h3>📚 Library</h3></div>', unsafe_allow_html=True)
        if st.button("Open Library"): 
            log_activity(st.session_state['user_email'], "Visit", "Library")
            navigate_to("Library")

# ==========================================
# 📑 PAGE: MOCK TEST
# ==========================================
elif st.session_state['current_page'] == "Test":
    if st.button("⬅️ Back"): navigate_to("Home")
    st.title("📑 Exam Simulator")
    
    if 'test_paper' not in st.session_state:
        c1, c2, c3 = st.columns(3)
        with c1: level = st.selectbox("Level", ["CA Final", "CA Inter"])
        with c2: subject = st.selectbox("Subject", CA_FINAL_SUBJECTS if level == "CA Final" else CA_INTER_SUBJECTS)
        with c3: diff = st.selectbox("Difficulty", ["Medium", "Hard"])
        
        if st.button("Generate Paper"):
            with st.spinner("Generating..."):
                prompt = f"Create 10 Q Mock Test for {level} {subject} ({diff}). No Answers."
                try:
                    res = model.generate_content(prompt)
                    st.session_state['test_paper'] = res.text
                    st.session_state['test_sub'] = subject
                    st.rerun()
                except: st.error("API Error")
    else:
        st.markdown(st.session_state['test_paper'])
        f = st.file_uploader("Upload Answers", accept_multiple_files=True)
        if f and st.button("Submit"):
            with st.spinner("Checking..."):
                imgs = [Image.open(i) for i in f]
                res = model.generate_content([f"Check this {st.session_state['test_sub']} paper strictly.", *imgs])
                st.markdown(res.text)
                save_score(st.session_state['user_email'], st.session_state['test_sub'], 40)
        if st.button("Reset"): del st.session_state['test_paper']; st.rerun()

# ==========================================
# 📸 PAGE: CHECKER
# ==========================================
elif st.session_state['current_page'] == "Checker":
    if st.button("⬅️ Back"): navigate_to("Home")
    st.title("📸 Checker")
    st.info("Upload Question & Answer")
    q = st.file_uploader("Question Img")
    a = st.file_uploader("Answer Img")
    if q and a and st.button("Check"):
        with st.spinner("Checking..."):
            res = model.generate_content(["Read Q, Check A", Image.open(q), Image.open(a)])
            st.markdown(res.text)

# ==========================================
# 🤖 PAGE: KUCHU
# ==========================================
elif st.session_state['current_page'] == "Kuchu":
    if st.button("⬅️ Back"): navigate_to("Home")
    st.title("🤖 Kuchu Chat")
    msg = st.text_input("Message")
    if st.button("Send"):
        res = model.generate_content(f"Act as Kuchu (Funny CA Friend). User: {msg}")
        st.write(f"Kuchu: {res.text}")

# ==========================================
# 📚 PAGE: LIBRARY
# ==========================================
elif st.session_state['current_page'] == "Library":
    if st.button("⬅️ Back"): navigate_to("Home")
    st.title("📚 Library")
    t = st.text_input("Enter Topic")
    if st.button("Get Notes"):
        res = model.generate_content(f"Revision Notes on: {t}")
        st.markdown(res.text)

# ==========================================
# 🕵️‍♂️ PAGE: ADMIN
# ==========================================
elif st.session_state['current_page'] == "Admin":
    if st.button("⬅️ Back"): navigate_to("Home")
    st.title("Admin Logs")
    st.dataframe(get_logs())
