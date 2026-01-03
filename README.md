# 🏥 MediTriage Pro: Multimodal Clinical Assistant

**MediTriage Pro** is an advanced Medical Decision Support System (CDSS) designed for rapid patient screening. By leveraging Multimodal LLMs and Vector Databases, the system analyzes both **symptom descriptions (text)** and **clinical photos (images)** to provide an immediate urgency rating and actionable guidance. 

**Live Demo:** [Try MediTriage Pro here](https://multimodal-medical-triage-assistant-chatbotgit.streamlit.app/)

---

## 🎨 Design Philosophy: Clinical Contrast
The application utilizes a professional "High-Contrast" theme designed for clarity:
* **Deep Navy Sidebar**: Contains control elements and visual upload tools, keeping the main workspace uncluttered.
* **Clean White Portal**: The main diagnostic area uses a crisp white background to ensure medical text and imagery are perfectly legible.
* **Visual Urgency Dial**: A dynamic, semi-circular gauge that provides a "at-a-glance" priority level for healthcare providers.

---

## 🚀 Key Features

* **Multimodal Analysis**: Processes text-based symptoms and image-based visual markers (rashes, wounds, etc.) simultaneously.
* **AI-Powered Triage**: Utilizes **Gemma-3-4B** (via OpenRouter) to categorize urgency according to clinical standards.
* **Visual Urgency Dial**: A dynamic, semi-circular gauge providing an instant visual cue of patient priority.
* **RAG-Enhanced Brain**: Integrates **Qdrant Cloud** and local **HuggingFace embeddings** for medical protocol retrieval.

---

## 🛠️ Tech Stack

| Component         | Technology                               |
| :---------------- | :--------------------------------------- |
| **Frontend** | Streamlit (Python)                       |
| **Orchestration** | LangChain 0.3                            |
| **LLM Gateway** | OpenRouter (Gemini / Gemma-3)            |
| **Vector DB** | Qdrant Cloud                             |
| **Embeddings** | HuggingFace (`all-MiniLM-L6-v2`)         |
| **Image Processing**| Pillow (PIL)                             |

---

## 📂 Project Structure

```text
├── app.py              # Main Streamlit UI & Custom CSS
├── brain.py            # TriageBrain Class (Logic & RAG)
├── requirements.txt    # Python Dependencies
├── .streamlit/         # Secrets Configuration (Local)
└── README.md           # Project Documentation
```

---

## ⚙️ Installation & Setup
**1. Clone the Repository**
Bash the below commands in your local machine's cmd terminal to clone and open the project in your IDE
* git clone https://github.com/thkash18/Multimodal-Medical-Triage-Assistant-ChatBot.git
* cd Multimodal-Medical-Triage-Assistant-ChatBot
* code .

**2. Install Dependencies**
Ensure you have Python 3.9+ installed, then run:
* pip install -r requirements.txt

**3. Configure Secrets**
Create a .streamlit/secrets.toml file for local development, or set these as Environment Variables on your cloud hosting platform:
* OPENROUTER_API_KEY = "sk-or-v1-..."
* QDRANT_URL = "your-qdrant-cluster-url"
* QDRANT_API_KEY = "your-qdrant-api-key"

**4. Run the Application**
* streamlit run app.py

---

## 📊 Triage Levels & Urgency Matrix

The system classifies patient assessments into five standardized priority levels based on clinical urgency and physiological stability. This ensures that life-threatening conditions are addressed with immediate priority.

| Level | Classification | Description | Clinical Action |
| :--- | :--- | :--- | :--- |
| 🔴 **1** | **CRITICAL** | Immediate Life-Threatening condition. | Immediate intervention required. |
| 🟠 **2** | **EMERGENT** | High risk; time-sensitive clinical markers. | Assessment within 15 minutes. |
| 🟡 **3** | **URGENT** | Acute but physiologically stable. | Assessment within 30-60 minutes. |
| 🔵 **4** | **NON-URGENT** | Minor or chronic conditions. | Routine clinical review. |
| 🟢 **5** | **ROUTINE** | Minor symptoms or maintenance care. | Home care or scheduled follow-up. |

---

### 🔍 How the Assessment Works
The **MediTriage Brain** uses a multi-step logic process to determine these levels:
1. **Visual Scan**: Analyzes uploaded photos for physical trauma, discoloration, or inflammation.
2. **Textual Extraction**: Parses keywords related to pain intensity, duration, and vital signs.
3. **Protocol Matching**: Compares inputs against clinical standards stored in the **Qdrant Vector Database**.
4. **Final Scoring**: Generates the urgency level which is then rendered on the dynamic **Urgency Dial** in the UI.

## ⚖️ Disclaimer
⚠️ NOT A SUBSTITUTE FOR PROFESSIONAL MEDICAL ADVICE. This tool is for educational and screening purposes only. It is designed to assist in urgency prioritization and does not provide medical diagnoses. In case of a life-threatening emergency, always contact local emergency services immediately.
