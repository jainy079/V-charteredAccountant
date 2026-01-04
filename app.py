import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 👇 APNI API KEY YAHAN PASTE KAR DO 👇
# (Taaki Vanshika ko baar-baar daalni na pade)
# ==========================================
GOOGLE_API_KEY = "AIzaSyCwjIu4Hc4HczJUeZdfVgw1j1VxWPZq-JM" 

# --- PAGE CONFIGURATION (Professional Look) ---
st.set_page_config(
    page_title="Vanshika's CA Workspace",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Sajawat) ---
st.markdown("""
<style>
    .main {
        background-color: #F5F7F9;
    }
    .stButton>button {
        width: 100%;
        background-color: #004B87;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #003366;
        color: white;
    }
    h1 {
        color: #004B87;
        font-family: 'Helvetica', sans-serif;
    }
    .big-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- GEMINI SETUP ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"API Key Error: {e}")

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=100)
    st.title("CA Final Toolkit")
    st.write("Welcome, **Vanshika!** 👩‍🎓")
    st.markdown("---")
    mode = st.radio("Select Tool:", 
        ["📝 Answer Checker (ICAI Mode)", 
         "🧠 Exam Quiz Generator", 
         "💡 Concept Explainer"]
    )
    st.markdown("---")
    st.info("⚡ Powered by Gemini 2.5")

# --- MAIN APP LOGIC ---

# 1. HEADER
st.markdown(f"<h1>{mode}</h1>", unsafe_allow_html=True)

# --- MODE 1: ANSWER CHECKER ---
if mode == "📝 Answer Checker (ICAI Mode)":
    st.markdown('<div class="big-card">Upload your handwritten answer. AI will check it strictly as per ICAI standards.</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("📸 Upload Answer Sheet", type=["jpg", "jpeg", "png"])
    
    col1, col2 = st.columns([1, 1])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        with col1:
            st.image(image, caption="Your Answer", use_column_width=True)
        
        with col2:
            if st.button("🔍 Check Answer Now"):
                with st.spinner("Acting as Strict Examiner..."):
                    try:
                        prompt = """
                        Act as a strict Examiner for ICAI (CA Final Level).
                        Analyze this handwritten answer image.
                        
                        Output Format:
                        1. **Topic Identified:** [Name]
                        2. **Mistakes:** [Bullet points of missing keywords/sections]
                        3. **Marks:** [Give score out of 5]
                        4. **Correct Answer:** [Rewrite the perfect answer in professional language]
                        """
                        response = model.generate_content([prompt, image])
                        st.success("Analysis Complete!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# --- MODE 2: QUIZ GENERATOR ---
elif mode == "🧠 Exam Quiz Generator":
    st.markdown('<div class="big-card">Generate tricky MCQs for any chapter.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("Enter Chapter/Topic Name (e.g., GST Audit, Forex)")
    with col2:
        num_q = st.number_input("Questions", min_value=1, max_value=10, value=5)
    
    if st.button("🎲 Generate Quiz"):
        if topic:
            with st.spinner(f"Creating {num_q} tricky questions on {topic}..."):
                try:
                    prompt = f"""
                    Create {num_q} CA Final level MCQs on topic: '{topic}'.
                    Questions should be scenario-based.
                    IMPORTANT: Do NOT show the answer immediately.
                    Format each question as:
                    **Q1:** Question text...
                    (A) Option 1
                    (B) Option 2
                    (C) Option 3
                    (D) Option 4
                    
                    <Hidden Answer Key at the bottom>
                    """
                    response = model.generate_content(prompt)
                    st.session_state['quiz_result'] = response.text
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a topic first.")

    # Show Quiz Result if available
    if 'quiz_result' in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state['quiz_result'])
        st.info("💡 Note: Answers are usually provided at the bottom of the generated text.")

# --- MODE 3: CONCEPT EXPLAINER ---
elif mode == "💡 Concept Explainer":
    st.markdown('<div class="big-card">Stuck on a concept? Ask here for a deep dive explanation.</div>', unsafe_allow_html=True)
    
    doubt = st.text_area("Type your doubt here...", height=150)
    
    if st.button("🚀 Explain Detail"):
        if doubt:
            with st.spinner("Searching Study Material & Case Laws..."):
                try:
                    prompt = f"""
                    Explain this CA Final concept strictly as per ICAI Study Material: '{doubt}'.
                    Include:
                    1. Definition / Provision
                    2. Relevant Section Numbers
                    3. Case Laws (if applicable)
                    4. Easy Example
                    """
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
