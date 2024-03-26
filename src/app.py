import os
from langchain_groq import ChatGroq
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

mixtral_llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")


def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
    db_uri = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'

    return SQLDatabase.from_uri(db_uri)


def get_sql_chain(db: SQLDatabase):
    """Write a SQL query based on the user query and the database schema."""

    template = """
    You are a helpful SQL assistant. You are helping a user run SQL queries on a database.
    Based on the database schema below, write a SQL query to help the user.
    You must take the history of the chat and use it to help the user.
    
    <database schema>{schema}</database schema>
    
    Conversation history: {chat_history}
    
    Write the SQL query and nothing else. Do not wrap the query in a code block or any other markdown formatting.
    
    Examples:
    User query: "What are the names of the Artist in the database?"
    SQL query: "SELECT FirstName, LastName FROM Artist"
    User query: "Which 3 artists have the most tracks?"
    SQL query: "SELECT ArtistId, COUNT(*) as TrackCount FROM Tracks GROUP BY ArtistId ORDER BY TrackCount DESC LIMIT 3"
    
    Your turn:
    User query: {user_query}
    SQL query: 
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = mixtral_llm

    def get_schema(_):
        return db.get_table_info()

    return (RunnablePassthrough.assign(schema=get_schema) | prompt | llm | StrOutputParser())


def get_response(user_query: str, db: SQLDatabase, chat_history: list):
    """Write a natural language response after running the SQL query."""

    sql_chain = get_sql_chain(db)

    template = """
    You are a helpful SQL assistant. You are helping a user run SQL queries on a database.
    Based on the database schema, chat history, user query and sql query, write a response to the user in a natural language.
    Limit your answer to just to result of the SQL query only.
    
    <database schema>{schema}</database schema>
    Conversation history: {chat_history}
    User query: {user_query}
    <sql query>{sql_query}</sql query>

    SQL response:{response}
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = mixtral_llm

    chain = (RunnablePassthrough.assign(sql_query=sql_chain).assign(
        schema=lambda _: db.get_table_info(),
        response=lambda vars: db.run(vars["sql_query"]))
        | prompt | llm | StrOutputParser())

    return chain.invoke({"chat_history": chat_history, "user_query": user_query})


def run_app():
    """Run the application."""

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(
                content="Hi there! I'm a SQL assistant. Ask me anything about your database.")
        ]

    # Retrieve the database password
    db_password = os.environ.get('DB1_PASSWORD')
    db_user = os.environ.get('DB_USER')
    db_host = os.environ.get('HOST')
    db_port = os.environ.get('PORT')
    db_database = os.environ.get('DATABASE')

    with st.sidebar:

        st.subheader(body="Settings")
        st.write(
            "This is an application using MySQL. Connect to the database and start chatting.")
        st.text_input("User:", value=db_user, key="user")
        st.text_input("Host:", value=db_host, key="host")
        st.text_input("Port:", value=db_port, key="port")
        st.text_input("Password:", type="password",
                      key="password", value=db_password)
        st.text_input("Database:", key="database", value=db_database)

        if st.button("Connect"):
            with st.spinner("Connecting to database..."):
                db = init_database(
                    user=st.session_state['user'],
                    password=st.session_state['password'],
                    host=st.session_state['host'],
                    port=st.session_state['port'],
                    database=st.session_state['database']
                )
                st.session_state.db = db
                st.success("Connected to database!")

    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)

    user_query = st.chat_input("Type here a message...")
    if user_query is not None and user_query.strip() != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))

        with st.chat_message("Human"):
            st.markdown(user_query)

        with st.spinner("Thinking..."):
            response = get_response(
                user_query, st.session_state.db, st.session_state.chat_history)
            st.session_state.chat_history.append(AIMessage(content=response))

        with st.chat_message("AI"):
            st.markdown(response)
