# 🏥 MediTriage Pro: Multimodal Clinical Assistant

**MediTriage Pro** is an advanced Medical Decision Support System (CDSS) designed for rapid patient screening. By leveraging Multimodal LLMs and Vector Databases, the system analyzes both **symptom descriptions (text)** and **clinical photos (images)** to provide an immediate urgency rating and actionable guidance.

---

## 🚀 Key Features

* **Multimodal Analysis**: Processes text-based symptoms and image-based visual markers (rashes, wounds, etc.) simultaneously.
* **AI-Powered Triage**: Utilizes **Gemma-3-4B** (via OpenRouter) to categorize urgency according to clinical standards.
* **Visual Urgency Dial**: A dynamic, semi-circular gauge providing an instant visual cue of patient priority.
* **RAG-Enhanced Brain**: Integrates **Qdrant Cloud** and local **HuggingFace embeddings** for medical protocol retrieval.
* **Modern Clinical UI**: A "Skyish Blue" frosted-glass interface optimized for ease of use in high-pressure environments.



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
