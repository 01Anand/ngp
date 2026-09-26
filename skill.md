# Streamlit Groq Chatbot Generator & Assistant Skill

## Purpose
This skill guides the generation, extension, and maintenance of a real-time conversational web interface using **Streamlit** and the **Groq API** in Python.


## Core Architecture & Patterns

When generating or refactoring code for this application, enforce the following patterns:

### 1. Environment & API Key Management
- Always use `python-dotenv` to load secrets from `.env`.
- Default to `os.getenv("GROQ_API_KEY", "")`.
- Provide a sidebar password input fallback for manual key entry, prefilled with the `.env` value.
- If `api_key` is missing when submitting a prompt, trigger `st.error()` and halt execution with `st.stop()`.

### 2. State & History Management
- Store conversation turns in `st.session_state.messages` as a list of dicts: `[{"role": "user" | "assistant", "content": "..."}]`.
- Re-render the existing chat history sequentially using `st.chat_message(role)`.
- Provide a "Clear Chat History" sidebar button that resets `st.session_state.messages = []` and calls `st.rerun()`.

### 3. Model Configuration & Parameters
Support standard Groq chat completion models:
- `openai/gpt-oss-120b` (Default)
- `meta-llama/llama-prompt-guard-2-86m`
- `mixtral-8x7b-32768`
- `gemma2-9b-it`

Expose controls via `st.sidebar`:
- `temperature`: Float slider (0.0 to 2.0, default: 0.7, step: 0.1).
- `max_tokens`: Int slider (128 to 8192, default: 2048, step: 128).

### 4. Streaming Execution Loop
- Instantiate the client using `Groq(api_key=api_key)`.
- Use `client.chat.completions.create(..., stream=True)`.
- Render the streaming output dynamically in an `st.empty()` container with a typing cursor (e.g., `▌`).
- Append the final aggregated response to `st.session_state.messages`.
- Wrap the API call in a `try...except Exception as e:` block and display errors using `st.error()`.

---

## Project Dependencies
Ensure output code assumes the following `requirements.txt`:
```text
streamlit
groq
python-dotenv
