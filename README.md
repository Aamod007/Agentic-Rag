# Agentic RAG API Backend

![AI Agent](./AI%20Agent.svg)

This repository provides a comprehensive, production-ready FastAPI backend demonstrating Agentic Retrieval-Augmented Generation (RAG). By combining standard RAG pipelines with autonomous tool-calling capabilities, this system enables large language models (LLMs) to answer context-specific questions and securely execute real-world actions on behalf of the user.

---

## Executive Summary

Standard RAG architectures improve language models by grounding their responses in retrieved documents. The typical lifecycle is strictly informational:
`Query → Retrieve → Answer`.

**Agentic RAG** expands this paradigm by integrating an autonomous reasoning loop, allowing the model to act as an intelligent agent. The extended lifecycle is:
`Query → Retrieve → Reason → Decide → Act → Answer`.

This system is capable of:
1. **Context Retrieval**: Querying a Supabase pgvector database for relevant institutional knowledge, policies, or constraints.
2. **Autonomous Reasoning**: Evaluating the user's intent against retrieved context to determine if external actions are required.
3. **Tool Execution**: Dynamically selecting and securely calling external APIs (e.g., Google Calendar for scheduling, Gmail for communications) based on precise parameters derived during the reasoning phase.
4. **Action Confirmation**: Delivering a cohesive final response that includes citations from the knowledge base and confirms the execution of requested actions.

---

## System Architecture

The codebase is organized to support scalability, strict type validation, and clear separation of concerns.

```text
launch-agentic-rag/
├── app/                              # Core Application Logic
│   ├── agents/                       # Orchestration & Tools
│   │   ├── orchestrator.py           # Main reasoning and execution loop 
│   │   └── tools/                    # Tool registry (Calendar, Email, etc.)
│   ├── services/                     # Business Logic (RAG pipeline, Chat, Embeddings)
│   ├── schemas/                      # Data Validation (Pydantic models & API schemas)
│   ├── config/                       # Application Settings (Database, Environment)
│   └── data/                         # Initial data seed and sample documents
├── devtools/                         # Debug utilities and testing scripts
├── sql/                              # Database schema setup (Supabase/pgvector)
├── static/                           # Static assets and Web Chat UI
├── credentials/                      # Secure storage for service accounts
├── main.py                           # FastAPI application entry point
├── requirements.txt                  # Python dependency specifications
└── Dockerfile                        # Containerization configuration
```

---

## Setup and Installation

### System Requirements
- Python 3.11 or higher
- Git
- Supabase account (for PostgreSQL and pgvector support)
- OpenAI API Key (or an equivalent supported provider)
- Google Cloud Platform Account (Optional, required for Calendar and Email integrations)

### 1. Local Environment Initialization

Clone the repository and initialize the Python virtual environment:

```bash
git clone https://github.com/ShenSeanChen/launch-agentic-rag.git
cd launch-agentic-rag

python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

pip install -r requirements.txt
```

### 2. Database Configuration

1. Create a new Supabase project to obtain your API credentials.
2. Navigate to the Supabase SQL Editor and execute the script provided in `sql/init_supabase.sql`. This provisions the `rag_chunks` table and configures the pgvector functions required for similarity search operations.

### 3. Environment Variables

Create the environment configuration file:

```bash
cp .env.example .env
```

Populate the `.env` file with your credentials:

```env
# Database Credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# AI Provider Credentials
OPENAI_API_KEY=sk-your_api_key
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o
AI_PROVIDER=openai

# Google API Credentials (Optional)
# Ensure your service account JSON file is placed securely in the credentials/ directory.
GOOGLE_SERVICE_ACCOUNT_PATH=credentials/service_account.json
GOOGLE_CALENDAR_EMAIL=your-email@example.com
GOOGLE_CALENDAR_ID=primary
```

*(Note: Utilizing Google Calendar or Email features requires a Google Cloud Service Account with appropriate API permissions and Domain-Wide Delegation if operating within Google Workspace).*

### 4. Verification and Execution

Validate the integrity of your local configuration using the bundled test suite:
```bash
python devtools/test_setup.py
```

Launch the FastAPI application server:
```bash
uvicorn main:app --reload --port 8000
```

Upon successful startup, the application interfaces are accessible at:
- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Web Chat Interface**: http://localhost:8000/chat

---

## API Reference

### 1. Standard RAG (`/answer`)
Facilitates traditional question-answering based strictly on the initialized knowledge base. No external actions are taken.
```bash
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the standard cancellation policy?"}'
```

### 2. Agentic Action (`/agent`)
Invokes the reasoning loop, allowing the agent to answer questions or execute registered tools as necessary.
```bash
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Schedule a preliminary consultation with client@example.com for tomorrow at 2 PM"
  }'
```

### 3. Contextual Agentic Action
Maintains conversational state by passing chat history, ensuring subsequent actions respect prior context.
```bash
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Update that meeting to 45 minutes",
    "chat_history": [
      {"role": "user", "content": "Schedule a call with client@example.com tomorrow"},
      {"role": "assistant", "content": "I can help with that. What duration should the meeting be?"}
    ]
  }'
```

---

## Extending Agent Capabilities

The system architecture is designed for extensibility. To register a custom tool:
1. Subclass the `BaseTool` class in `app/agents/tools/`, implementing the `name`, `description`, and `execute` methods.
2. Register the newly created tool instance within `app/agents/tools/registry.py`.
3. Define the tool's JSON schema in `app/schemas/tool_schemas.py` to ensure the LLM correctly structures the required parameters during invocation.

---

## Deployment Strategies

### Docker Deployment

The application is fully containerized for consistent deployment across environments:
```bash
docker build -t agentic-rag .
docker run -p 8080:8080 --env-file .env agentic-rag
```

### Cloud Run Deployment

To deploy the service to Google Cloud Run:
1. Push the compiled Docker image to Google Artifact Registry.
2. Provision a Secret in Google Secret Manager to securely store your `service_account.json` file.
3. Deploy the Cloud Run service, mounting the provisioned secret as a volume at `/app/credentials/service_account.json` and injecting all required environment variables.

---

## License
This project is provided under the MIT License. Please refer to the [LICENSE](LICENSE) file for comprehensive legal details.
