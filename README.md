# MEU (Middle East University) Chatbot

## 💡 Idea of the Project
This project is an intelligent AI-powered chatbot designed specifically for the Middle East University (MEU) in Jordan. It serves as a 24/7 virtual assistant to help students, prospective applicants, and visitors easily find information regarding the university. 

The chatbot provides instant answers about:
- University administration (President, Board of Trustees, Deans)
- Academic programs (Bachelor's, Master's, Diplomas, and International Programs)
- Admission requirements, procedures, and required GPA
- Credit hour pricing, fees, and available discounts/scholarships
- University facilities (recreational, health, transportation, etc.)
- Contact information and registration links

## ⚙️ How It Works
The chatbot is built using a **Retrieval-Augmented Generation (RAG)** architecture to ensure accurate and up-to-date responses based solely on the university's official data:

1. **Data Ingestion**: Official university data is scraped and stored in a structured JSON file (`meu_data.json`).
2. **Chunking & Embedding**: The application parses the JSON data into logical text chunks and generates vector embeddings for each chunk using OpenAI's embedding models.
3. **Semantic Retrieval**: When a user asks a question, their query is embedded into a vector. The system calculates the cosine similarity between the query vector and the knowledge base vectors to retrieve the most relevant context.
4. **Context-Aware Response Generation**: The retrieved context, along with the user's recent conversation history, is sent to OpenAI's LLM (`gpt-4o-mini`). The model is strictly prompted to answer based only on the provided context, ask for clarification if needed, and gracefully handle out-of-context queries.
5. **Multi-Channel Delivery**: The chatbot can be accessed via a built-in web interface or through Facebook Messenger via a dedicated webhook.
6. **Administrative Logging**: Chat logs are stored in a Firebase Firestore database, allowing administrators to monitor interactions via a secure admin dashboard.

## 🛠️ Technology Stack
- **Backend Framework**: Python, Flask
- **AI & NLP**: OpenAI API (`gpt-4o-mini` for chat completions, `text-embedding-3-small` for embeddings)
- **Vector Search**: Custom Python implementation using Cosine Similarity
- **Database & Logging**: Firebase Admin SDK (Firestore)
- **Deployment**: Supports Windows IIS (using `wfastcgi` and `web.config`) as well as WSGI servers like `gunicorn` (via `Procfile`)
- **Environment Management**: `python-dotenv` for secure secret management

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- An OpenAI API Key
- A Firebase Service Account Key (for logging and admin features)
- A Facebook Page Access Token (optional, for Messenger integration)

### Installation
1. **Clone the repository** (if applicable) and navigate to the project directory:
   ```bash
   cd "chatBot v.3"
   ```

2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables**:
   Create a `.env` file in the root directory and add the following:
   ```env
   SECRET_KEY=your_flask_secret_key
   OPENAI_API_KEY=your_openai_api_key
   FB_VERIFY_TOKEN=your_facebook_verify_token
   FB_PAGE_ACCESS_TOKEN=your_facebook_page_access_token
   ```

4. **Set up Firebase**:
   Place your Firebase service account JSON file in the root directory and name it `firebase-key.json`.

5. **Run the Application**:
   ```bash
   python app.py
   ```
   Or use a WSGI server like waitress or gunicorn for production.

## 🗂️ Project Structure
- `app.py`: The main Flask application containing the core logic, API endpoints, and RAG implementation.
- `requirements.txt`: Python dependencies.
- `scrap website data/`: Directory containing the web scraping scripts and the output `meu_data.json` knowledge base.
- `templates/`: HTML templates for the web chat interface and admin dashboard.
- `static/`: CSS, JS, and image assets for the web interface.
- `verify_*.py`: Various utility scripts used for debugging and verifying specific aspects of the data and chatbot functionality.

## 🔒 Security
- All sensitive keys are managed via environment variables.
- The admin dashboard is protected by a login system.
- Facebook Webhook endpoints use verification tokens to ensure requests originate from Meta.
