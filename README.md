# LangGraph Chatbot

A Streamlit chatbot project with Groq chat inference and several LangGraph
examples: basic chat, SQLite-backed conversation threads, tool use, PDF
question answering with retrieval-augmented generation (RAG), and MCP tools.
The tool-enabled variants also include a SQLite-backed task manager.

## Features

- Groq chat model configured with `GROQ_API_KEY` and optional `GROQ_MODEL`.
- Search, calculator, and Alpha Vantage stock quote tools.
- Add, list, complete, and delete tasks in the current conversation.
- Separate example frontends for basic chat, streaming, SQLite history, tools,
  PDF RAG, and MCP.
- PDF text extraction and local embeddings with FastEmbed, indexed in FAISS.

## Setup

Run these commands in this project directory in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `GROQ_API_KEY` to your own key. Add other API keys only for
tools you plan to use. Never commit `.env` or share its contents.

## Run an app

Start one frontend at a time:

```powershell
streamlit run streamlit_frontend_tool.py
```

Other examples include `streamlit_frontend.py`,
`streamlit_frontend_database.py`, `streamlit_rag_frontend.py`, and
`streamlit_frontend_mcp.py`. See [chatbotlanggraph.txt](chatbotlanggraph.txt)
for the full project and interview guide, including each frontend's backend,
memory behavior, tools, limitations, and setup notes.

## Local data and privacy

SQLite chat checkpoints and tasks are stored in `chatbot.db` and are ignored by
Git. They remain on the machine running the app. A shared deployment needs
authentication and user-level access controls before conversation histories or
tasks can be considered private between users.

The basic in-memory example loses its conversation state when its process
stops. The RAG example's PDF vector index is also held in process memory and
must be rebuilt after a restart.

## Notes

This project contains multiple educational app variants. Review dependencies,
external service requirements, and any applicable source licenses before
redistributing or deploying it.
