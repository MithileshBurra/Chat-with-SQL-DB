import streamlit as st
import sqlite3
from pathlib import Path

from sqlalchemy import create_engine
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler


st.set_page_config(
    page_title = "CHAT_WITH_SQL_DB",
    page_icon="🦜",
    layout = "wide"
)
st.title("🦜 LangChain: Chat with SQL DB")

LOCALDB = "USE_LOCALDB"
MYSQL   = "USE_MYSQL"

st.sidebar.header("Configuration")
db_options = st.sidebar.radio(
    "Choose your database",
    options=["SQLite — student.db (local)", "MySQL (remote)"],
)

if db_options == "MySQL (remote)":
    db_uri = MYSQL
    st.sidebar.subheader("MySQL connection details")
    mysql_host     = st.sidebar.text_input("Host",     placeholder="localhost")
    mysql_user     = st.sidebar.text_input("Username", placeholder="root")
    mysql_password = st.sidebar.text_input("Password", type="password")
    mysql_db       = st.sidebar.text_input("Database", placeholder="school")

else:
    db_uri = LOCALDB
st.sidebar.subheader("Groq API key")
api_key = st.sidebar.text_input("Key", type="password", label_visibility="collapsed")

missing = []
if not api_key:
    missing.append('GROQ API KEY is missing')

if db_uri == MYSQL and not all([mysql_host, mysql_user, mysql_password, mysql_db]):
    missing.append("All four MySQL fields are required")

if missing:
    for msg in missing:
        st.warning(msg)
    st.stop()

@st.cache_resource
def get_llm(api_key):
    return ChatGroq(
        groq_api_key = api_key,
        model = "llama-3.3-70b-versatile",
        streaming = True
    )
llm = get_llm(api_key)


@st.cache_resource(ttl = "2h")
def configure_db(db_uri, mysql_host = None,mysql_user = None,mysql_password=None,mysql_db=None) -> SQLDatabase:

    if db_uri == LOCALDB:

        db_path = (Path(__file__).parent/"student.db").absolute()

        if not db_path:
            st.error(f"student.db not found at: {db_path}")
            st.stop()

        creator = lambda: sqlite3.connect(f"file:{db_path}?mode=ro", uri = True)
        return SQLDatabase(create_engine("sqlite:///", creator = creator))

    connection_str = (
        f"mysql+mysqlconnector://{mysql_user}:{mysql_password}"
        f"@{mysql_host}/{mysql_db}"
    )
    try:
        engine = create_engine(connection_str)
        return SQLDatabase(engine)
    except Exception as e:
        st.error(f"Could not connect to MySQL: {e}")
        st.stop()

if db_uri == MYSQL:
   db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = configure_db(db_uri)



@st.cache_resource
def get_agent(_db, _llm):

    
    try:
        toolkit = SQLDatabaseToolkit(db=_db, llm=_llm)
        agent = create_sql_agent(
            llm=_llm,
            toolkit=toolkit,
            agent_type="zero-shot-react-description",
            verbose=True,
            handle_parsing_errors=True,
        )
        return agent

    except Exception as e:
        st.error(f"Agent failed to build: {e}")
        return None

agent = get_agent(db,llm)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role":"assistant", "content":"Hello! Ask me anything about the database."}
    ]

col1,col2 = st.columns([6,1])
with col2:
   if st.button("clear_history",use_container_width = True):
    st.session_state.messages = [{"role":"assistant","content":"Chat cleared. Ask me anything"}]
    st.rerun()

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask anything about the database…")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    st.chat_message("user").write(user_input)

    with st.chat_message("assistant"):
        callbacks = [StreamlitCallbackHandler(st.container(),expand_new_thoughts = False)]

    try:
        response = agent.run(user_input, callbacks = callbacks)
    except Exception as e:
        response = f"Something went wrong while running the agent: {e}"
        st.error(response)

    st.session_state.messages.append({"role":"assitant","content":response})
    st.write(response)









