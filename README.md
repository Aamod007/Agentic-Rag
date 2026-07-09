# 🤖 Agentic RAG AI Backend

![AI Agent](./AI%20Agent.svg)

A comprehensive, production-ready FastAPI backend demonstrating **Agentic RAG**. This project combines the power of Retrieval-Augmented Generation (RAG) with autonomous tool-calling capabilities. Instead of just answering questions, the AI agent can autonomously reason about user intent, fetch necessary context, and take real-world actions like scheduling meetings or sending emails.

---

## 🌟 What is Agentic RAG?

Traditional RAG processes end after answering a query based on retrieved context. The standard workflow is:
`Query → Retrieve → Answer`.

**Agentic RAG** takes this significantly further by giving the LLM a framework to think, decide, and act. The workflow becomes:
`Query → Retrieve → Reason → Decide → Act → Answer`.

### The Agentic Workflow in Detail

1. **User Query**: The user asks a question or requests an action (e.g., "Schedule a 30-minute consultation with john@example.com for tomorrow at 2 PM").
2. **Context Retrieval**: The system queries the vector database (Supabase pgvector) for relevant company policies, availability constraints, or context related to the user's request.
3. **Reasoning Loop**: The LLM acts as an autonomous agent. It evaluates the user's prompt against the retrieved context to determine if it needs to take an action.
4. **Decision & Tool Calling**: If an action is required, the LLM decides which tool to use (e.g., Google Calendar tool, Email tool) and generates the correct parameters based on the query and the retrieved context (like knowing that "consultation calls are 30 minutes long" from the database).
5. **Execution**: The backend automatically executes the selected tool using the generated parameters.
6. **Final Answer**: The agent observes the result of the tool execution and formulates a final, human-readable response, complete with citations of the documents it used and confirmation of the actions taken.

---

## 📁 Project Architecture

The codebase is structured for scalability and separation of concerns:

```text
launch-agentic-rag/
├── app/                              # Core Application Logic
│   ├── agents/                       # Orchestration & Tools
│   │   ├── orchestrator.py           # Main reasoning loop 
│   │   └── tools/                    # Tool registry (Calendar, Email)
│   ├── services/                     # Business Logic (RAG pipeline, Chat, Embeddings)
│   ├── schemas/                      # Data Validation (Pydantic models & API schemas)
│   ├── config/                       # Settings (Database, Env variables)
│   └── data/                         # Initial data & sample documents
├── devtools/                         # Debug utilities and testing scripts
├── sql/                              # Database schema setup (Supabase/pgvector)
├── static/                           # Frontend assets (Chat UI)
├── credentials/                      # Credentials (e.g., GCP Service Account)
├── main.py                           # Application entry point
├── requirements.txt                  # Python dependencies
└── Dockerfile                        # Containerization setup
```

---

## 🚀 Setup Guide

### Prerequisites
- **Python 3.11+**
- **Git**
- **Supabase Account** for PostgreSQL and pgvector.
- **OpenAI API Key** (or Anthropic API key).
- **Google Cloud Account** (Optional, required if you want to use the Calendar and Email tools).

### 1. Installation

```bash
git clone https://github.com/ShenSeanChen/launch-agentic-rag.git
cd launch-agentic-rag

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install required dependencies
pip install -r requirements.txt
```

### 2. Configure Database (Supabase)

1. Create a new Supabase project and navigate to your project settings to find your API keys.
2. Open the Supabase SQL Editor and run the contents of the `sql/init_supabase.sql` file. This initializes the `rag_chunks` table and sets up the necessary pgvector functions for similarity search.

### 3. Environment Setup

Copy the environment template and fill in your specific details:

```bash
cp .env.example .env
```

Open `.env` and configure your credentials:

```env
# Database Credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...

# AI Provider Credentials
OPENAI_API_KEY=sk-...
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o
AI_PROVIDER=openai

# Google API Credentials (Optional)
# Place your service account JSON file in the credentials/ folder
GOOGLE_SERVICE_ACCOUNT_PATH=credentials/service_account.json
GOOGLE_CALENDAR_EMAIL=your-email@example.com
GOOGLE_CALENDAR_ID=primary
```

*(Note: To use Google Calendar/Email features, you must create a Service Account in Google Cloud, enable Domain-Wide Delegation if using Workspace, and download the JSON key).*

### 4. Verify & Run

Validate your setup using the included test script:
```bash
python devtools/test_setup.py
```

Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```

Once running, you can access the application at:
- **Swagger API Docs**: http://localhost:8000/docs
- **Web Chat Interface**: http://localhost:8000/chat

---

## 🔌 API Endpoints

### 1. Traditional RAG (`/answer`)
Answers questions strictly based on the knowledge base without taking actions.
```bash
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{"query": "What is your return policy?"}'
```

### 2. Agentic RAG (`/agent`)
Combines RAG with function calling. The agent will autonomously decide whether to answer the question, or execute tools like scheduling a meeting.
```bash
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Schedule a consultation call with john@example.com for tomorrow at 2pm"
  }'
```

### 3. Multi-turn Agentic RAG
The agent supports conversational history to maintain context across multiple interactions.
```bash
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Make it 30 minutes instead",
    "chat_history": [
      {"role": "user", "content": "Schedule a call with john@example.com tomorrow"},
      {"role": "assistant", "content": "I can help. How long should it be?"}
    ]
  }'
```

---

## 🛠 Adding Custom Tools

You can easily extend the agent's capabilities by adding new tools to `app/agents/tools/`:
1. Subclass `BaseTool` and implement the `name`, `description`, and `execute` methods.
2. Register the tool in `app/agents/tools/registry.py`.
3. Add the JSON schema to `app/schemas/tool_schemas.py` so the LLM understands what parameters it requires.

---

## ☁️ Deployment

### Docker

You can containerize the application easily:
```bash
docker build -t agentic-rag .
docker run -p 8080:8080 --env-file .env agentic-rag
```

### Cloud Run

To deploy to Google Cloud Run:
1. Push your Docker image to Google Artifact Registry.
2. Create a Secret in Google Secret Manager containing your `service_account.json` file.
3. Deploy the service to Cloud Run, ensuring you mount the secret as a volume at `/app/credentials/service_account.json` and set your environment variables accordingly.

---

## 📄 License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
