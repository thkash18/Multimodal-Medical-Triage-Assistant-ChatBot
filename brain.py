# brain.py (Updated for LangChain 0.3+)
import re
import os
from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
import qdrant_client.http.models as qmodels
from qdrant_client import QdrantClient
import base64
from io import BytesIO

class TriageBrain:
    def __init__(self, api_key, qdrant_url, qdrant_api_key):
        self.llm = ChatOpenAI(
            model="google/gemma-3-27b-it", # Or your preferred Gemma variant
            openai_api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://your-app-url.com", # Required by OpenRouter
                "X-Title": "MediTriage Assistant"
            }
        )
        
        # 2. Local Embeddings (Safe for Deployment)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # 3. Vector DB Setup
        self.client_qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key,)
        self.collection_name = "triage_deploy_v1"

        self.collection_name = "medical_logs"
        # --- ADD THIS LOGIC TO CREATE THE COLLECTION ---

        # Check if collection exists, if not, create it
        collections = self.client_qdrant.get_collections().collections
        if any(c.name == self.collection_name for c in collections):
        # Delete the old one because it has the wrong dimensions (768)
            self.client_qdrant.delete_collection(collection_name=self.collection_name)

        self.client_qdrant.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(
                size=384, 
                distance=qmodels.Distance.COSINE
            ),
        )
        # -----------------------------------------------

        self.vector_store = QdrantVectorStore(
            client=self.client_qdrant,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )
        self.history = []
        # self.system_instruction = "..." # Your medical triage prompt
         # 4. The "Master" Triage Instructions
        self.system_instruction = """
        NOTICE: This is an AI-generated advisory, not a medical diagnosis. 
        If you are experiencing chest pain, difficulty breathing, or severe bleeding, call 911 immediately.
        
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



    def get_urgency_score(self, response_text):
        """
        Parses the AI response to find the LEVEL X mentioned.
        Returns an integer 1-5, or 5 as a safe default.
        """
        match = re.search(r"LEVEL (\d)", response_text.upper())
        if match:
            return int(match.group(1))
        return 5 # Default to 'Routine' if not found
    


    def process_triage(self, user_text, pil_image=None):
        # 1. Prepare message content list
        content = [{"type": "text", "text": user_text}]

        # 2. Convert PIL Image to Base64 String if provided
        if pil_image:
            buffered = BytesIO()
            # Ensure we save in a format the API understands
            pil_image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # OpenRouter/OpenAI specific image format
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_str}"
                }
            })

        # 3. Construct messages
        messages = [
            SystemMessage(content=self.system_instruction),
            # Add history here if you are using it
            HumanMessage(content=content)
        ]

        # 4. Invoke LLM
        response = self.llm.invoke(messages)
        response_text = response.content

        # --- ADD THIS EXTRACTION LOGIC ---
        # 1. Look for "LEVEL 1", "LEVEL 2", etc. in the AI's response
        match = re.search(r"LEVEL\s*([1-5])", response_text.upper())

        # 2. If found, convert to integer. If not, default to 5 (Routine)
        if match:
            urgency_score = int(match.group(1))
        else:
            urgency_score = 5 
        # ---------------------------------

        # Now this will work because urgency_score is defined!
        return response_text, urgency_score


    



   