# Streamlit Groq RAG Chatbot Generator & Assistant Skills

## Purpose

This skill file is for creating a **Streamlit** and **Groq** RAG (Retrieval-Augmented Generation) Chatbot in Python using **ChromaDB** for local vector storage and semantic search.

---

## Core Architecture & Patterns

When generating or refactoring code for this application, enforce the following patterns:

### 1. Environment & API Key Management
* Use a `.env` file to store sensitive keys (`GROQ_API_KEY`).
* Use the `python-dotenv` library via `load_dotenv()`.
* Validate API keys upon application startup. If an API key is missing or invalid, display a clear UI error message using `st.error()` and halt execution.

### 2. RAG Pipeline & ChromaDB Integration
* **Document Ingestion:** Support loading local documents (PDFs/TXTs) using a text splitter (e.g., recursive character splitting) into chunks.
* **Vector Store:** Use `chromadb` as the persistent vector database (`chromadb.PersistentClient`).
* **Embeddings:** Generate vector embeddings for document chunks using an embedding model (e.g., SentenceTransformers / `all-MiniLM-L6-v2` or HuggingFace embeddings).
* **Retrieval Flow:**
  1. Capture user prompt from `st.chat_input()`.
  2. Query ChromaDB to retrieve the top $K$ relevant text chunks based on similarity search.
  3. Inject retrieved chunks into the Groq LLM system context prompt alongside the user's query.

### 3. State & History Management
* Maintain full conversation history using `st.session_state.messages`.
* Persist vector store client instances using `@st.cache_resource` to avoid re-initializing ChromaDB on every UI rerun.
* Include a sidebar button to clear chat history and re-index or clear documents from ChromaDB.

### 4. Model Configuration & Parameters
Support key Groq models in a sidebar dropdown:
* `llama-3.3-70b-versatile`
* `llama-3.1-8b-instant`

Provide interactive UI controls:
* **Temperature:** `st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)`
* **Max Tokens:** `st.slider("Max Tokens", 128, 8192, 2048, 128)`
* **Top-K Retrieval:** `st.slider("Retrieved Documents (K)", 1, 10, 3, 1)`

### 5. Streaming Execution Loop
* Initialize the Groq client using `groq.Groq(api_key=...)`.
* Stream LLM responses dynamically using `st.write_stream()` or token-by-token iteration (`client.chat.completions.create(..., stream=True)`).
* Wrap vector retrieval and API calls inside `try-except` blocks, capturing exceptions cleanly with `st.error()`.
* **Theme/Styling:** Enforce a clean, lightweight light mode theme layout (white background) with custom CSS injected via `st.markdown()` if needed.

---

## Project Dependencies

Ensure the following packages are listed in `requirements.txt`:

```text
streamlit
groq
chromadb
sentence-transformers
python-dotenv
langchain-text-splitters
pypdf
