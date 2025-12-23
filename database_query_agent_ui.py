import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tools.schema_tools import *
from state.agent_state import *
from graph.main_workflow import app
from tools.chart_tools import *

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Data Analysis Agent", page_icon=":robot_face:", layout="wide")
# Initialize session state
if "schema" not in st.session_state:
    st.session_state.schema = None
if "engine" not in st.session_state:
    st.session_state.engine = None
if "SessionLocal" not in st.session_state:
    st.session_state.SessionLocal = None

# Sidebar for database connection
st.sidebar.header("Database Connection")
db_type = st.sidebar.selectbox("Database Type", ["postgresql", "mysql"])
host = st.sidebar.text_input("Host", value="localhost")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
port = st.sidebar.text_input("Port")
database = st.sidebar.text_input("Database Name")

# Button to connect to database
if st.sidebar.button("Connect to Database"):
    try:
        if db_type == "postgresql":
            db_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        elif db_type == "mysql":
            db_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

        # Create engine and session
        st.session_state.engine = create_engine(db_url)
        st.session_state.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=st.session_state.engine)

        st.session_state.schema = get_database_schema(st.session_state.engine)
        st.sidebar.success("Connected to database and schema retrieved!")
    except Exception as e:
        st.sidebar.error(f"Failed to connect: {str(e)}")
        
# Main interface
st.title(":robot_face: Database Query Assistant")

# Query input
if st.session_state.schema:
    question = st.text_input("Enter your question:")
    if st.button("Submit Question") and question:
        with st.spinner("Processing your question..."):
            initial_state = {
                "question": question,
                "sql_query": "",
                "query_result": "",
                "query_rows": [],
                "attempts": 0,
                "relevance": "",
                "sql_error": False
            }
            result = app.invoke(initial_state)

            # Display results
            st.subheader("Results")
            st.write("*Query Result:*")
            st.write(result["query_result"])

            st.write("*Query Rows:*")
            if result["query_rows"]:
                st.json(result["query_rows"])
            else:
                st.write("No rows returned.")

            # Display chart
            st.subheader("Chart")

            try:
                fig = drawing_chart(question, result)
                if fig:
                    st.pyplot(fig)
                else:
                    st.write("No chart generated (no data returned).")
            except:
                st.write("No chart generated for single-column result.")

else:
    st.warning("Please connect to a database first using the sidebar.")