# 🦜 Chat with SQL DB — Natural Language SQL Agent

A conversational AI app that translates plain English questions into SQL queries, executes them against a database, and returns natural language answers — powered by LangChain, Llama 3, and Streamlit.

---

## What This Project Does

Most people can't write SQL. This app removes that barrier entirely. You ask a question the way you'd ask a colleague — *"Who scored the highest marks?"* or *"How many students are older than 20?"* — and the agent handles everything underneath: inspecting the schema, writing the query, running it, and forming a coherent answer.

No SQL knowledge required from the user. No hardcoded queries. Every question is answered dynamically.

---

## Demo

> **User:** Who scored the highest marks?

```
Thought: I need to find the student with the maximum marks. Let me check the schema first.
Action: sql_db_schema
Observation: Table 'students' has columns: id, name, age, marks, grade

Thought: Now I can write the query.
Action: sql_db_query
Action Input: SELECT name, marks FROM students ORDER BY marks DESC LIMIT 1
Observation: [('Diana', 95)]

Final Answer: Diana scored the highest marks with 95.
```

> **Assistant:** Diana scored the highest marks with 95.

The agent's full reasoning chain streams live into the UI — every thought, every query, every observation — before the final answer appears.

---

## Architecture

```
User Question
      ↓
 Streamlit UI
      ↓
 LangChain SQL Agent (ReAct loop)
      ↓                    ↓
 LLM Reasoning       SQL Toolkit
 (Llama 3 via Groq)       ↓
                     SQLAlchemy Engine
                          ↓
                    SQLite / MySQL
```

The agent follows the **ReAct pattern** — Reasoning and Acting in alternating steps. It doesn't guess at an answer. It inspects the actual schema, writes SQL based on what it finds, runs it, reads the result, and only then forms a response. If its first query is wrong, it reasons about why and tries again.

---

## Technical Decisions Worth Noting

**Why Groq instead of OpenAI?**
Groq's LPU hardware runs Llama 3 at 300-500 tokens/second — fast enough that streaming feels genuinely real-time rather than a loading animation. For a chat interface where responsiveness matters, this was the right trade-off over raw model capability.

**Why read-only SQLite?**
The local database connection uses SQLite's `?mode=ro` URI flag — opened at the driver level via a custom `creator` lambda rather than through SQLAlchemy's standard URL. This means the agent physically cannot run `INSERT`, `UPDATE`, `DELETE`, or `DROP` regardless of what the LLM decides to do. Safety enforced at the database layer, not the prompt layer.

**Why cache the LLM, DB, and agent separately?**
Streamlit reruns the entire script on every user interaction. Without `@st.cache_resource`, a new LLM client, database connection, and agent would be instantiated on every single keypress. Each is cached independently so they survive reruns without reconnecting or rebuilding.

**Why `handle_parsing_errors=True`?**
Llama 3 8B occasionally drifts from the strict ReAct format the agent parser expects — especially on ambiguous or multi-step questions. Without this flag, a single malformed LLM response crashes the agent. With it, the parsing error is fed back to the LLM as a correction and the agent retries. Essential for stability with smaller open-source models.

**Why underscore-prefixed args in `get_agent(_db, _llm)`?**
`@st.cache_resource` hashes function arguments to determine cache hits. LangChain objects like `SQLDatabase` and `ChatGroq` aren't hashable. The leading underscore tells Streamlit to skip hashing those arguments — a Streamlit-specific convention, not standard Python.

---

## Tech Stack

| | Technology |
|---|---|
| **UI** | Streamlit |
| **LLM** | Llama 3 8B (8192 context window) |
| **Inference** | Groq API |
| **Agent** | LangChain SQL Agent — ReAct, zero-shot |
| **ORM** | SQLAlchemy 2.0 |
| **Local DB** | SQLite 3 (read-only) |
| **Remote DB** | MySQL via mysql-connector-python |
| **Streaming** | StreamlitCallbackHandler |

---

## Key Implementation Details

- Dual database support — SQLite for local development, MySQL for remote/production databases, selectable at runtime from the sidebar
- Full input validation with `st.stop()` — the app halts before instantiating any LangChain objects if the API key or database credentials are missing, preventing cascading errors
- `student.db` existence check before connection — surfaces a clear error immediately rather than a cryptic SQLAlchemy failure deep in the stack
- Agent and toolkit built inside a cached function — the ReAct agent is expensive to construct; caching ensures it's built once per session
- Streamed thoughts collapsed by default — `expand_new_thoughts=False` on `StreamlitCallbackHandler` keeps the UI clean; reasoning steps are visible but not overwhelming

---

## What I Learned Building This

Working through this project gave me a deep understanding of how LangChain's agent execution model actually works under the hood — not just how to use `create_sql_agent()` but what the ReAct loop is doing at each step, why the toolkit needs both the `db` and `llm` objects, and how `StreamlitCallbackHandler` hooks into LangChain's callback system to stream intermediate steps.

The debugging process was equally instructive — tracing import path changes across LangChain 1.x, understanding why `@st.cache_resource` requires hashable arguments, and learning why Streamlit's rerun model makes `st.session_state` non-negotiable for anything stateful.

---

## Repository Structure

```
ST_SQL_CHATBOT/
├── app.py            # complete application
├── student.db        # local SQLite database
├── requirements.txt
└── README.md
```

---

## Dependencies

```
streamlit>=1.58.0
langchain>=1.3.10
langchain-community>=0.4.2
langchain-groq>=1.1.3
sqlalchemy>=2.0.51
mysql-connector-python>=9.7.0
python-dotenv>=1.2.2
```

---

*Built by Mithilesh Burra — [github.com/MithileshBurra](https://github.com/MithileshBurra)*
