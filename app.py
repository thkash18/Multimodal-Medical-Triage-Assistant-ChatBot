import streamlit as st
from PIL import Image
from brain import TriageBrain
import os

def draw_urgency_dial(level):
    # Map levels to colors and labels
    colors = {1: "#FF0000", 2: "#FF8C00", 3: "#FFD700", 4: "#1E90FF", 5: "#32CD32"}
    labels = {1: "CRITICAL", 2: "EMERGENT", 3: "URGENT", 4: "NON-URGENT", 5: "ROUTINE"}
    
    # Calculate visual fill (Level 1 is 100% full/red, Level 5 is 20% full/green)
    fill_percent = (6 - level) * 20 
    
    dial_html = f"""
    <div style="text-align: center; font-family: sans-serif;">
        <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 5px;">URGENCY SCORE</div>
        <div style="width: 150px; height: 75px; background: #E2E8F0; border-radius: 150px 150px 0 0; position: relative; margin: 0 auto; overflow: hidden;">
            <div style="width: 150px; height: 75px; background: {colors[level]}; border-radius: 150px 150px 0 0; 
                        transform-origin: bottom; transform: rotate({(fill_percent/100)*180 - 180}deg); 
                        transition: transform 1s ease-out;"></div>
            <div style="position: absolute; top: 15px; left: 15px; width: 120px; height: 60px; background: white; border-radius: 120px 120px 0 0; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 5px;">
                <span style="font-size: 1.5rem; font-weight: bold; color: {colors[level]};">{level}</span>
            </div>
        </div>
        <div style="font-weight: bold; color: {colors[level]}; margin-top: 5px; font-size: 0.9rem;">{labels[level]}</div>
    </div>
    """
    return dial_html

# --- 1. CONFIG & STATE ---
st.set_page_config(page_title="MediTriage Pro", page_icon="🏥", layout="wide")

# Crucial: Initialize history FIRST to avoid AttributeErrors
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "triage_brain" not in st.session_state:
    api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    q_url = st.secrets.get("QDRANT_URL")
    q_key = st.secrets.get("QDRANT_API_KEY")
    
    if not all([api_key, q_url, q_key]):
        st.error("⚠️ Configuration Missing (API Keys/URL)")
        st.stop()
    st.session_state.triage_brain = TriageBrain(api_key, q_url, q_key)

# --- 2. CUSTOM CSS FOR CLINICAL LOOK ---
st.markdown("""
    <style>
    /* Main background */
    .stApp { background-color: #F8FAFC; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] { background-color: #0F172A; color: white; }
    
    /* Header styling */
    .main-header {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border-left: 8px solid #0EA5E9;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }

    /* FIX: Chat Message Text Visibility */
    .stChatMessage { 
        border-radius: 12px; 
        border: 1px solid #E2E8F0; 
        background-color: white !important; 
        color: #1E293B !important; /* Forces dark text for visibility */
    }

    /* Optional: Ensure markdown text inside messages is also dark */
    .stChatMessage div[data-testid="stMarkdownContainer"] p {
        color: #1E293B !important;
    }

    /* Fix for the user input text color */
    .stTextInput input {
        color: #1E293B;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("## 🏥 MediTriage Pro")
    st.caption("Clinical Decision Support System")
    st.divider()
    
    st.markdown("### 📸 Visual Assessment")
    uploaded_file = st.file_uploader(
        "Upload symptom image", 
        type=["jpg", "png"], 
        key="image_uploader",
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.image(uploaded_file, caption="Symptom Photo", use_container_width=True)
        # Store in session state so the Brain can access it once
        st.session_state.pending_image = Image.open(uploaded_file)
    else:
        st.session_state.pending_image = None
    
    st.divider()
    if st.button("🔄 Reset Patient Session", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# --- 4. MAIN PORTAL ---
st.markdown("""
    <div class="main-header">
        <h1 style='margin:0; color:#1E293B;'>Triage Assessment Portal</h1>
        <p style='margin:0; color:#64748B;'>Advanced AI Screening for Immediate Clinical Guidance</p>
    </div>
    """, unsafe_allow_html=True)

# Display History
# --- 4. MAIN INTERFACE: DISPLAY HISTORY ---
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and "level" in msg:
            # Create two columns for assistant messages
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(msg["content"], unsafe_allow_html=True)
            with col2:
                # Use the helper function we created
                st.markdown(draw_urgency_dial(msg["level"]), unsafe_allow_html=True)
        else:
            # Standard display for user messages
            st.markdown(msg["content"], unsafe_allow_html=True)

# --- 5. INTERACTION ---
# --- 5. CHAT INPUT & PROCESSING ---
if prompt := st.chat_input("Describe the emergency or symptoms..."):
    # Store and display user message
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process and display AI response
    with st.chat_message("assistant"):
        with st.status("Analyzing clinical indicators...") as status:
            img = Image.open(uploaded_file) if uploaded_file else None
            response_text, urgency_level = st.session_state.triage_brain.process_triage(prompt, img)
            status.update(label=f"Assessment Complete", state="complete")
        
        # Display with the side-by-side Dial layout
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(response_text, unsafe_allow_html=True)
        with col2:
            st.markdown(draw_urgency_dial(urgency_level), unsafe_allow_html=True)
        
        # Save level to history so it persists on refresh
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": response_text, 
            "level": urgency_level
        })

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #64748B; font-size: 0.8rem;">
        ⚠️ <b>Disclaimer:</b> This AI assistant is for screening purposes only and does not constitute medical advice. 
        In case of a life-threatening emergency, call your local emergency services immediately.
        <br>Developed for <b> Medical Triage Project</b>
    </div>
    """, 
    unsafe_allow_html=True
)