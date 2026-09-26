import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pypdf

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Groq RAG Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Light Theme CSS (Clean white background)
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #1e293b;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .main-header h1 {
        color: #0f172a;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 0.25rem 0;
    }
    .main-header p {
        color: #64748b;
        font-size: 0.95rem;
        margin: 0;
    }
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-active {
        background-color: #dcfce7;
        color: #166534;
    }
    .status-missing {
        background-color: #fee2e2;
        color: #991b1b;
    }
    .doc-stats {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e40af;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Cached ChromaDB Vector Database Initialization
# ---------------------------------------------------------
@st.cache_resource
def get_vector_store():
    # Persistent ChromaDB client
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # SentenceTransformer embedding function (all-MiniLM-L6-v2)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Get or create vector collection
    collection = chroma_client.get_or_create_collection(
        name="rag_documents",
        embedding_function=embedding_func
    )
    return chroma_client, collection

chroma_client, collection = get_vector_store()

# Helper function to extract text from PDF or TXT files
def extract_text_from_file(file) -> str:
    text = ""
    if file.name.endswith(".pdf"):
        pdf_reader = pypdf.PdfReader(file)
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    elif file.name.endswith(".txt"):
        text = file.getvalue().decode("utf-8")
    return text

# Read API Key from environment
env_api_key = os.getenv("GROQ_API_KEY", "")

# ---------------------------------------------------------
# Sidebar Configuration & Parameters
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://groq.com/wp-content/uploads/2024/03/PBG-mark1-orange.png", width=40)
    st.title("📚 Groq RAG Config")
    st.markdown("---")

    # API Key Input
    api_key_input = st.text_input(
        "Groq API Key",
        value=env_api_key,
        type="password",
        help="Enter your Groq API Key or configure GROQ_API_KEY in your .env file."
    )

    effective_api_key = api_key_input.strip() if api_key_input else env_api_key.strip()
    if effective_api_key:
        st.markdown('<div class="status-badge status-active">🟢 API Key Ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-missing">🔴 API Key Missing</div>', unsafe_allow_html=True)

    st.markdown("### 📄 Document Ingestion")
    uploaded_files = st.file_uploader(
        "Upload PDF or TXT Documents",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        help="Upload documents to index into ChromaDB for semantic search retrieval."
    )

    if uploaded_files:
        if st.button("📥 Index Documents", use_container_width=True):
            with st.spinner("Processing & embedding document chunks..."):
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                total_chunks = 0
                
                for uploaded_file in uploaded_files:
                    file_text = extract_text_from_file(uploaded_file)
                    if file_text.strip():
                        chunks = text_splitter.split_text(file_text)
                        ids = [f"{uploaded_file.name}_{uuid.uuid4().hex[:8]}_{i}" for i in range(len(chunks))]
                        metadatas = [{"source": uploaded_file.name, "chunk_index": i} for i in range(len(chunks))]
                        
                        collection.add(
                            documents=chunks,
                            metadatas=metadatas,
                            ids=ids
                        )
                        total_chunks += len(chunks)
                
                st.success(f"Indexed {total_chunks} chunks from {len(uploaded_files)} file(s) into ChromaDB!")

    # Display current vector collection document count
    current_doc_count = collection.count()
    st.markdown(f'<div class="doc-stats">📊 Indexed Chunks in ChromaDB: <b>{current_doc_count}</b></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ Model Parameters")

    # Active Groq Models with Custom Input support
    model_options = [
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "deepseek-r1-distill-llama-70b",
        "qwen-qwq-32b",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "Custom Model..."
    ]

    selected_model_choice = st.selectbox(
        "Select Groq Model",
        options=model_options,
        index=0,
        help="Choose a Groq LLM or enter a custom model ID."
    )

    if selected_model_choice == "Custom Model...":
        selected_model = st.text_input("Enter Custom Model ID", value="deepseek-r1-distill-llama-70b")
    else:
        selected_model = selected_model_choice



    # Temperature Slider (0.0 to 1.0 per skill_updated.md)
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Controls randomness. Lower is more deterministic, higher is creative."
    )

    # Max Tokens Slider
    max_tokens = st.slider(
        "Max Tokens",
        min_value=128,
        max_value=8192,
        value=2048,
        step=128,
        help="Maximum length of generated response."
    )

    # Top-K Retrieval Slider (1 to 10 per skill_updated.md)
    top_k = st.slider(
        "Retrieved Documents (K)",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
        help="Number of document chunks to retrieve from ChromaDB for context."
    )

    st.markdown("---")

    # Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("⚠️ Reset Vector DB", use_container_width=True):
            try:
                chroma_client.delete_collection("rag_documents")
                st.session_state.collection = chroma_client.get_or_create_collection(
                    name="rag_documents",
                    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
                )
                st.success("Vector DB cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Error resetting vector DB: {str(e)}")

# ---------------------------------------------------------
# Main Interface Header
# ---------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>📚 Groq RAG Assistant</h1>
    <p>Retrieval-Augmented Generation using ChromaDB semantic search & Groq LLM inference</p>
</div>
""", unsafe_allow_html=True)

# Initialize Chat Messages History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if prompt := st.chat_input("Ask a question based on your uploaded documents..."):
    # Append user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check API key presence
    if not effective_api_key:
        st.error("⚠️ **Groq API Key is missing!** Please enter your key in the sidebar or configure `GROQ_API_KEY` in the `.env` file.")
    else:
        with st.chat_message("assistant"):
            try:
                # -----------------------------------------------------
                # 1. RAG Vector Retrieval Flow
                # -----------------------------------------------------
                retrieved_chunks = []
                chunk_sources = []
                
                if collection.count() > 0:
                    results = collection.query(
                        query_texts=[prompt],
                        n_results=min(top_k, collection.count())
                    )
                    if results and "documents" in results and results["documents"]:
                        retrieved_chunks = results["documents"][0]
                        if "metadatas" in results and results["metadatas"]:
                            chunk_sources = results["metadatas"][0]

                # -----------------------------------------------------
                # 2. System Context Prompt Construction
                # -----------------------------------------------------
                if retrieved_chunks:
                    context_str = "\n\n---\n\n".join(
                        [f"[Source: {meta.get('source', 'Document')} | Chunk {meta.get('chunk_index', i)}]\n{chunk}" 
                         for i, (chunk, meta) in enumerate(zip(retrieved_chunks, chunk_sources))]
                    )
                    system_prompt = f"""You are an intelligent RAG assistant. Answer the user's question accurately using ONLY the retrieved document context below.
If the answer cannot be determined from the context, state clearly that the provided documents do not contain sufficient information.

Retrieved Document Context:
{context_str}"""
                else:
                    system_prompt = "You are a helpful AI assistant powered by Groq. (Note: No document context was found in ChromaDB)."

                # -----------------------------------------------------
                # 3. Groq Streaming LLM Execution
                # -----------------------------------------------------
                client = Groq(api_key=effective_api_key)
                
                messages_payload = [{"role": "system", "content": system_prompt}]
                for msg in st.session_state.messages:
                    messages_payload.append({"role": msg["role"], "content": msg["content"]})

                def generate_stream():
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=messages_payload,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True
                    )
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            yield delta

                # Render response stream dynamically
                full_response = st.write_stream(generate_stream())

                # Display retrieved context expander for transparency
                if retrieved_chunks:
                    with st.expander("📚 View Retrieved Context Chunks from ChromaDB"):
                        for idx, (chunk, meta) in enumerate(zip(retrieved_chunks, chunk_sources)):
                            st.markdown(f"**Chunk {idx+1}** *(Source: `{meta.get('source', 'Unknown')}`)*")
                            st.info(chunk)

                # Save assistant response to session state
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"❌ **Error during RAG execution**: {str(e)}")
