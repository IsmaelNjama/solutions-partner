# Solutions Partner

## 1. Search Companion

Solutions Partner is an AI-powered research companion built on LangGraph that intelligently routes user queries to the right information source. When a user asks a question, a lightweight router model classifies it into one of three categories:

- **query_docs** — retrieves relevant information from a Milvus vector database containing Risco alarm panel documentation
- **web_search** — performs a real-time web search via Tavily for current or external information
- **out_of_scope** — general conversation handled directly by the agent

After retrieval or search, a main agent model synthesizes the results into a clear, accurate answer. The backend exposes both streaming and non-streaming endpoints via FastAPI, and a separate UI repository provides the frontend.

## 2. Prerequisites

- **Python 3.10+**
- **Git**
- **Nebius Token Factory** — provides OpenAI-compatible API access to all LLM and embedding models. Create an account and generate an API key at the [Nebius Token Factory](https://studio.nebius.ai/).

## 3. Installation

```bash
# Clone the repository
git clone https://github.com/IsmaelNjama/solutions-partner.git
cd solutions-partner

# Create and activate a virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv sync
```

## 4. Environment Configuration

Create a `.env` file in the project root and fill in your credentials:

```env
# Nebius Token Factory — powers all LLM and embedding calls
NEBIUS_API_KEY=your_nebius_api_key

# Tavily — web search API
TAVILY_API_KEY=your_tavily_api_key

# Milvus cluster — vector database for RAG document retrieval
SERVING_CLUSTER_ENDPOINT=your_milvus_cluster_endpoint
TOKEN=your_milvus_auth_token

# LangSmith — LLM observability and tracing
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=your_project_name
```

## 5. Running the Server

```bash
uv run uvicorn app.main:app --reload
```

The API server starts at `http://localhost:8000`. Available endpoints:

| Method | Path            | Description                                          |
| ------ | --------------- | ---------------------------------------------------- |
| POST   | `/agent`        | Non-streaming — returns the full response at once    |
| POST   | `/agent/stream` | Streaming — returns tokens as newline-delimited JSON |
| GET    | `/health`       | Health check                                         |

Interactive API docs are available at `http://localhost:8000/docs`.

## 6. Starting the UI

Open a **new terminal** and run:

```bash
# Clone the UI repository
git clone https://github.com/IsmaelNjama/solutions-partner-ui.git
cd solutions-partner-ui

# Install dependencies and start the dev server
npm install
npm run dev
```

The UI connects to the backend API server. Make sure the backend server (step 5) is running before starting the UI.

## 7. Model Selection

All models are accessed through the Nebius Token Factory via an OpenAI-compatible API.

| Role       | Model                              | Why it was chosen                                                                                                                                                                                                                         |
| ---------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Main agent | `Qwen/Qwen3-30B-A3B-Instruct-2507` | A 30B Mixture-of-Experts model with only 3B active parameters per token, balancing strong reasoning and instruction-following with efficient inference. Ideal for synthesizing retrieved context into coherent answers.                   |
| Router     | `google/gemma-3-27b-it`            | A capable instruction-tuned model run at `temperature=0.0` with `max_tokens=20` for fast, deterministic query classification. The router only outputs a short label, so a mid-size model provides reliable structured output at low cost. |
| Embeddings | `Qwen/Qwen3-Embedding-8B`          | An 8B embedding model that produces high-quality vector representations for semantic search over technical documentation stored in Milvus.                                                                                                |

## 8. Project Structure

```
solutions-partner/
├── app/
│   ├── main.py                 # FastAPI app setup and CORS configuration
│   ├── api/
│   │   ├── routes.py           # Agent endpoints (streaming and non-streaming)
│   │   ├── schemas.py           # Request/response Pydantic models
│   │   └── services.py          # Agent invocation and token streaming logic
│   ├── agent/
│   │   └── agent.py             # LangChain agent builder
│   ├── graph/
│   │   └── workflow.py          # LangGraph workflow: router → retrieval/search → agent
│   ├── router/
│   │   └── router.py            # Router chain for query classification
│   ├── llm/
│   │   ├── llm.py               # Main agent LLM configuration
│   │   └── router_llm.py        # Router LLM configuration
│   ├── prompts/
│   │   └── prompts.py           # System and router prompts
│   ├── schemas/
│   │   └── schemas.py           # Route schema (query_docs | web_search | out_of_scope)
│   ├── services/
│   │   ├── rag_service.py       # Milvus retrieval for technical documentation
│   │   └── search_service.py    # Tavily web search and result formatting
│   ├── clients/
│   │   └── tavily.py            # Tavily search client
│   ├── rag/
│   │   └── ingest_docs.py       # PDF ingestion and chunking into Milvus
│   ├── tools/
│   │   └── tools.py             # Tool definitions (currently disabled)
│   └── utils/
│       ├── context.py          # Agent context schema
│       └── get_secrets_utils.py # Secrets loading (AWS Secrets Manager or .env)
├── infra/                       # AWS CloudFormation templates
├── .github/workflows/          # CI/CD pipeline
├── task-definition.json         # AWS ECS task definition (env vars and container config)
├── pyproject.toml              # Project dependencies and metadata
├── uv.lock                    # Locked dependency versions
└── README.md
```
