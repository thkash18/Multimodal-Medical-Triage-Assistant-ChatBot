import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="MediTriage AI", page_icon="🏥", layout="centered")

# --- CUSTOM CSS FOR STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    .urgency-box { padding: 15px; border-radius: 10px; color: white; font-weight: bold; text-align: center; margin: 10px 0; }
    .level-1 { background-color: #ff4b4b; } /* Critical - Red */
    .level-2 { background-color: #ff7675; } /* Emergent - Light Red */
    .level-3 { background-color: #fdcb6e; } /* Urgent - Orange */
    .level-4 { background-color: #55efc4; } /* Non-Urgent - Green */
    .level-5 { background-color: #74b9ff; } /* Routine - Blue */
    </style>
    """, unsafe_allow_html=True)

# --- AI SETUP ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def get_urgency_level(text):
    # Helper to pick out the level from the AI's response to color the box
    for i in range(1, 6):
        if f"LEVEL {i}" in text.upper():
            return i
    return 5

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏥 MediTriage AI")
    st.info("Upload a photo of your concern (rash, wound, label) and describe your symptoms.")
    uploaded_file = st.file_uploader("Upload Medical Image", type=["jpg", "jpeg", "png"])
    if st.button("Clear Chat"):
        st.session_state.messages = []

# --- CHAT INTERFACE ---
st.title("Medical Triage Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Describe your symptoms..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing symptoms and images..."):
            # Load image if exists
            image_data = None
            if uploaded_file:
                image_data = PIL.Image.open(uploaded_file)
            
            # Use the detailed prompt from our previous step
            system_instruction = """
            ### ROLE
            You are a Multimodal Medical Triage Advisory Assistant. Your goal is to help users assess the urgency of their symptoms or injuries based on text descriptions and visual inputs. You are professional, concise, and cautious.
            
            ### MANDATORY SAFETY PROTOCOLS
            1. DISCLAIMER: Every single response MUST begin with this exact text in bold: "**NOTICE: This is an AI-generated advisory, not a medical diagnosis. If you are experiencing chest pain, difficulty breathing, or severe bleeding, call emergency services (e.g., 911) immediately.**"
            2. NON-DIAGNOSTIC: Never say "You have [Disease]." Instead, say "Your symptoms are consistent with [Condition], which requires [Urgency Level] attention."
            3. NO PRESCRIPTIONS: Never recommend specific dosages or prescription medications. You may only suggest general over-the-counter comfort measures (e.g., "keep the wound clean") if appropriate for low-urgency cases.
            
            ### RESPONSE STRUCTURE
            Keep responses under 200 words. Use the following format:
            1. **Mandatory Disclaimer**
            2. **Urgency Rating**: Choose ONE from the scale below.
            3. **Brief Analysis**: 2-3 sentences describing what you observe in the text/image. Mention specific "red flags" (e.g., "The redness appears to be spreading," or "The description of 'crushing' pain is concerning").
            4. **Recommended Action**: Clear instructions on where the user should go (ER, Urgent Care, or Primary Doctor).
            
            ### URGENCY SCALE (Based on ESI)
            - [LEVEL 1: CRITICAL] Life-threatening. Immediate resuscitation required. (e.g., Unconscious, heart attack signs).
            - [LEVEL 2: EMERGENT] High risk. Potential for rapid deterioration. (e.g., Severe pain, head injury, deep wound).
            - [LEVEL 3: URGENT] Stable but needs multiple resources. (e.g., Possible broken bone, moderate infection).
            - [LEVEL 4: NON-URGENT] Stable, requires single resource. (e.g., Simple rash, minor cut, sore throat).
            - [LEVEL 5: ROUTINE] Minimal care needed. (e.g., Medication refill, cold symptoms).
            
            ### MULTIMODAL GUIDELINES
            When an image is provided:
            - Analyze visual markers: Color, swelling, discharge, or deformity.
            - If the image is too blurry to provide a safe assessment, state: "The image provided is unclear. Please provide a high-resolution photo in good lighting for a better assessment."
            """
            
            # Call Gemini
            response = client.models.generate_content(
                model="gemma-3-4b-it",
                contents=[system_instruction, prompt, image_data] if image_data else [system_instruction, prompt]
            )
            
            full_response = response.text
            level = get_urgency_level(full_response)
            
            # Visual Urgency Meter
            st.markdown(f'<div class="urgency-box level-{level}">ASSESSED URGENCY: LEVEL {level}</div>', unsafe_allow_html=True)
            
            st.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})