# EduWay AI Career Planner (Backend Engine)

The AI engine of the EduWay platform, built using Streamlit and LangChain. It uses AI models to evaluate skills, recommend learning roadmaps, and generate interactive assessments.

## 🌐 Live Access
- **AI Career Planner Engine:** [https://eduway.streamlit.app/](https://eduway.streamlit.app/)
- **Landing Page (Frontend):** [https://eduway-ai-career-path.vercel.app](https://eduway-ai-career-path.vercel.app)

## 🚀 How to Run Locally

### Prerequisites
- Python 3.11 (Recommended)
- Git

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/RohanThakre7/TechXL-EduWay.git
   cd TechXL-EduWay
   ```

2. **Set up virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Start the Streamlit Application:**
   ```bash
   streamlit run app_new.py
   ```
   Open [http://localhost:8501](http://localhost:8501) in your browser.

## 🛠️ Tech Stack & Libraries
- **Framework:** Streamlit
- **LLM Integration:** LangChain Core, LangChain Community, langchain-google-genai
- **Generative AI Model:** Google Gemini 3.5 Flash
- **Vector Search:** FAISS (for profile matching)
