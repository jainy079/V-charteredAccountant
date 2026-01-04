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
# 🛡️ SETUP
# ==========================================
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        st.error("🚨 API Key Missing!")
        st.stop()
except Exception as e:
    st.error(f"Setup Error: {e}")

st.set_page_config(
    page_title="V-Chartered",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded" # Desktop par khula rahega
)

# ==========================================
# 🧠 SMART API HANDLER (Retry Logic)
# ==========================================
def ask_gemini(prompt, image=None):
    try:
        if image: return model.generate_content([prompt, image])
        return model.generate_content(prompt)
    except:
        time.sleep(2)
        try:
            if image: return model.generate_content([prompt, image])
            return model.generate_content(prompt)
        except: return None

# ==========================================
# 💾 DATABASE
# ==========================================
def init_db():
    conn = sqlite3.connect('vchartered_db.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS results (email TEXT, subject TEXT, score INTEGER, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs (email TEXT, action TEXT, details TEXT, timestamp TEXT)''')
    conn.commit(); conn.close()

def log_activity(email, action, details=""):
    try:
        conn = sqlite3.connect('vchartered_db.db'); c = conn.cursor()
        c.execute("INSERT INTO activity_logs VALUES (?, ?, ?, ?)", (email, action, details, str(datetime.datetime.now())))
        conn.commit(); conn.close()
    except: pass

def get_leaderboard():
    conn = sqlite3.connect('vchartered_db.db')
    df = pd.read_sql_query("SELECT email, subject, score FROM results ORDER BY score DESC LIMIT 5", conn)
    conn.close()
    return df

init_db()

# ==========================================
# 🎨 HYBRID CSS (DESKTOP VS MOBILE MAGIC) 🪄
# ==========================================
if 'theme' not in st.session_state: st.session_state['theme'] = 'dark'

if st.session_state['theme'] == 'dark':
    bg_color = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"
    card_bg = "rgba(30, 41, 59, 0.9)"
    text_color = "#f8fafc"
    title_color = "#38bdf8"
    nav_bg = "rgba(15, 23, 42, 0.95)"
else:
    bg_color = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
    card_bg = "rgba(255, 255, 255, 0.95)"
    text_color = "#1a1a1a"
    title_color = "#004B87"
    nav_bg = "rgba(255, 255, 255, 0.95)"

st.markdown(f"""
<style>
    .stApp {{ background: {bg_color}; }}
    h1, h2, h3, h4, p, div, span, label, li {{ color: {text_color} !important; }}
    
    /* === DESKTOP DEFAULT === */
    /* Sidebar dikhega, Bottom Bar nahi dikhega */
    .bottom-nav-container {{ display: none !important; }}
    
    /* === MOBILE MODE (Jab screen choti ho) === */
    @media (max-width: 768px) {{
        /* Sidebar Chhupa do */
        [data-testid="stSidebar"] {{ display: none !important; }}
        
        /* Bottom Bar Dikha do */
        .bottom-nav-container {{ display: flex !important; }}
        
        /* Padding taaki content bottom bar ke neeche na chhipe */
        .block-container {{ padding-bottom: 80px; }}
        
        /* Header chota karo */
        .splash-title {{ font-size: 40px !important; }}
    }}

    /* Card Design */
    .feature-card {{
        background: {card_bg}; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1);
        text-align: center; margin-bottom: 15px;
    }}
    .feature-card h3 {{ color: {title_color} !important; }}

    /* Buttons */
    .stButton>button {{
        background: {title_color} !important; color: white !important;
        border-radius: 10px; border: none; padding: 10px 20px; width: 100%;
    }}

    /* Chat Messages */
    .stChatMessage {{ background: {card_bg}; border: 1px solid rgba(255,255,255,0.1); }}

    /* Bottom Nav Style */
    .bottom-nav-container {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: {nav_bg}; backdrop-filter: blur(10px);
        border-top: 1px solid rgba(255,255,255,0.1);
        z-index: 99999; padding: 10px 0;
        justify-content: space-around;
        box-shadow: 0 -4px 10px rgba(0,0,0,0.3);
    }}
    .nav-btn {{
        background: none; border: none; color: {text_color}; font-size: 24px; cursor: pointer;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🚀 NAVIGATION LOGIC
# ==========================================
def go_to(page):
    current_uid = st.query_params.get("uid", None)
    params = {"page": page}
    if current_uid: params["uid"] = current_uid
    st.query_params.update(params)
    time.sleep(0.05)
    st.rerun()

current_page = st.query_params.get("page", "Home")

# ==========================================
# 🔐 AUTH & SIDEBAR (Desktop ke liye)
# ==========================================
if 'user_email' not in st.session_state: st.session_state['user_email'] = None

# URL Auth
if "uid" in st.query_params:
    try:
        decoded = base64.b64decode(st.query_params["uid"]).decode('utf-8')
        if st.session_state['user_email'] != decoded:
            st.session_state['user_email'] = decoded
            st.rerun()
    except: pass

# LOGIN
if not st.session_state['user_email']:
    st.markdown(f"<h1 style='text-align:center; color:{title_color} !important;'>V-Chartered</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                # Demo Login
                encoded = base64.b64encode(email.encode()).decode()
                st.query_params["uid"] = encoded
                st.query_params["page"] = "Home"
                st.session_state['user_email'] = email
                st.rerun()
    st.stop()

# SIDEBAR (Sirf Desktop pe dikhega - CSS handle karega)
with st.sidebar:
    st.title("👤 Dashboard")
    st.write(f"User: {st.session_state['user_email']}")
    if st.button("🏠 Home"): go_to("Home")
    if st.button("📑 Mock Test"): go_to("Test")
    if st.button("📸 Checker"): go_to("Checker")
    if st.button("🤖 Kuchu Chat"): go_to("Kuchu")
    if st.button("📚 Library"): go_to("Library")
    
    st.markdown("---")
    if st.button("🌗 Theme"):
        st.session_state['theme'] = 'light' if st.session_state['theme'] == 'dark' else 'dark'
        st.rerun()
    if st.button("Logout"):
        st.query_params.clear()
        st.session_state['user_email'] = None
        st.rerun()
        
    st.markdown("### 🏆 Leaderboard")
    lb = get_leaderboard()
    if not lb.empty:
        for i, r in lb.iterrows(): st.write(f"🥇 {r['score']} - {r['email']}")

# ==========================================
# 🏠 MAIN SCREENS
# ==========================================
if current_page == "Home":
    st.markdown(f"<h2 style='color:{title_color} !important;'>Welcome Back! 👋</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="feature-card"><h3>📚 Library</h3><p>AI Revision Notes</p></div>', unsafe_allow_html=True)
        if st.button("Open Library", key="h_lib"): go_to("Library")
    with c2:
        st.markdown('<div class="feature-card"><h3>📸 Scanner</h3><p>Check Answers</p></div>', unsafe_allow_html=True)
        if st.button("Open Scanner", key="h_scan"): go_to("Checker")
        
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="feature-card"><h3>📑 Mock Test</h3><p>Exam Simulation</p></div>', unsafe_allow_html=True)
        if st.button("Start Test", key="h_test"): go_to("Test")
    with c4:
        st.markdown('<div class="feature-card"><h3>🤖 Kuchu</h3><p>AI Friend</p></div>', unsafe_allow_html=True)
        if st.button("Chat Now", key="h_chat"): go_to("Kuchu")

elif current_page == "Kuchu":
    st.title("🤖 Kuchu Chat")
    if "msgs" not in st.session_state: st.session_state.msgs = []
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])
    if p := st.chat_input("Message..."):
        st.session_state.msgs.append({"role":"user", "content":p})
        with st.chat_message("user"): st.write(p)
        res = ask_gemini(f"Act as funny CA friend. User: {p}")
        if res:
            st.session_state.msgs.append({"role":"assistant", "content":res.text})
            with st.chat_message("assistant"): st.write(res.text)

elif current_page == "Test":
    st.title("📑 Mock Test")
    if st.button("Generate Paper"):
        with st.status("Creating Paper..."):
            time.sleep(2)
            st.write("Paper Generated! (Mock)")

elif current_page == "Checker":
    st.title("📸 Answer Checker")
    img = st.file_uploader("Upload Image")
    if img and st.button("Check"): st.info("Checking...")

elif current_page == "Library":
    st.title("📚 Library")
    t = st.text_input("Topic")
    if t and st.button("Search"):
        with st.status("Searching..."):
            res = ask_gemini(f"Notes on {t}")
            if res: st.write(res.text)

# ==========================================
# 📱 MOBILE BOTTOM NAV (Hidden on Desktop)
# ==========================================
# Ye HTML block sirf Mobile par dikhega (CSS handle kar raha hai)
st.markdown("""
<div class="bottom-nav-container">
    <div style="display:none">
        </div>
</div>
""", unsafe_allow_html=True)

# THE TRICK: Floating Streamlit Buttons for Mobile
# Hum Streamlit ke columns ko fixed position de denge mobile ke liye
st.markdown("""
<style>
@media (max-width: 768px) {
    /* Target the last row of buttons */
    div[data-testid="stVerticalBlock"] > div:last-child {
        position: fixed; 
        bottom: 0; 
        left: 0; 
        width: 100%; 
        background: #1e293b; /* Match Theme */
        z-index: 9999;
        display: flex;
        justify-content: space-around;
        padding: 10px 0;
        border-top: 1px solid #334155;
    }
    /* Hide the text to make them icon-like if needed, or keep small */
    div[data-testid="stVerticalBlock"] > div:last-child button {
        border-radius: 50%;
        width: 50px;
        height: 50px;
        padding: 0;
        background: transparent !important;
        border: none !important;
        font-size: 20px;
    }
}
@media (min-width: 769px) {
    /* Hide these specific mobile buttons on desktop */
    div[data-testid="stVerticalBlock"] > div:last-child {
        display: none;
    }
}
</style>
""", unsafe_allow_html=True)

# Ye buttons sirf Mobile CSS se 'Bottom Bar' ban jayenge
# Desktop par ye 'display: none' ho jayenge
if st.session_state['user_email']:
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1: 
        if st.button("🏠", key="mob_home"): go_to("Home")
    with m_col2: 
        if st.button("📑", key="mob_test"): go_to("Test")
    with m_col3: 
        if st.button("🤖", key="mob_chat"): go_to("Kuchu")
    with m_col4: 
        if st.button("👤", key="mob_prof"): go_to("Home") # Profile
