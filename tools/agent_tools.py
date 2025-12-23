import streamlit as st 
from langchain_core.prompts import ChatPromptTemplate
import os 
from langchain_openai import ChatOpenAI
from sqlalchemy import text
from langchain_core.output_parsers import StrOutputParser
from state.prompt_templates import *
from state.agent_state import *
from env.api_key import *


# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0.5)

# Workflow functions (adapted to use session_state.schema)
def check_relevance(state: AgentState):
    question = state["question"]
    schema = st.session_state.schema
    system = """You are an assistant that determines whether a given question is related to the following database schema.

Schema:
{schema}

Respond with only "relevant" or "not_relevant".
""".format(schema=schema)
    human = f"Question: {question}"
    check_prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    structured_llm = llm.with_structured_output(CheckRelevance)
    relevance_checker = check_prompt | structured_llm
    relevance = relevance_checker.invoke({})
    state["relevance"] = relevance.relevance
    return state


def convert_nl_to_sql(state: AgentState):
    question = state["question"]
    schema = st.session_state.schema
    system = """You are an assistant that converts natural language questions into SQL queries based on the following schema:

{schema}

The current question is '{question}'. Ensure that all query-related data is scoped to this question.

Provide only the SQL query without any explanations. Alias columns appropriately to match the expected keys in the result.

For example, alias 'food.name' as 'food_name' and 'food.price' as 'price'.
""".format(schema=schema, question=question)
    convert_prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "Question: {question}")])
    structured_llm = llm.with_structured_output(ConvertToSQL)
    sql_generator = convert_prompt | structured_llm
    result = sql_generator.invoke({"question": question})
    state["sql_query"] = result.sql_query
    return state


def execute_sql(state: AgentState):
    sql_query = state["sql_query"].strip()
    session = st.session_state.SessionLocal()
    try:
        result = session.execute(text(sql_query))
        if sql_query.lower().startswith("select"):
            rows = result.fetchall()
            columns = result.keys()
            if rows:
                state["query_rows"] = [dict(zip(columns, row)) for row in rows]
                query_result = f"{len(state['query_rows'])} rows found."
            else:
                state["query_rows"] = []
                query_result = "No results found"
            state["query_result"] = query_result
            state["sql_error"] = False
        else:
            session.commit()
            state["query_result"] = "The action has been successfully completed."
            state["sql_error"] = False
    except Exception as e:
        state["query_result"] = f"Error executing SQL query: {str(e)}"
        state["sql_error"] = True
    finally:
        session.close()
    return state


def generate_human_readable_answer(state: AgentState):
    sql = state["sql_query"]
    result = state.get("query_rows", [])
    sql_error = state.get("sql_error", False)
    system = """You are an assistant that converts SQL query results into clear, natural language responses without including any identifiers like IDs."""
    if sql_error:
        generate_prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", """SQL Query:\n{sql}\nResult:\n{result}\nFormulate a clear and understandable error message in a single sentence.""")
        ])
    elif sql.lower().startswith("select"):
        if not result:
            generate_prompt = ChatPromptTemplate.from_messages([
                ("system", system),
                ("human", """SQL Query:\n{sql}\nResult:\n{result}\nFormulate a clear and understandable answer to the original question in detail.""")
            ])
        else:
            generate_prompt = ChatPromptTemplate.from_messages([
                ("system", system),
                ("human", """SQL Query:\n{sql}\nResult:\n{result}\nFormulate a clear and understandable answer to the original question in detail.""")
            ])
    else:
        generate_prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", """SQL Query:\n{sql}\nResult:\n{result}\nFormulate a clear and understandable confirmation message in detail.""")
        ])
    formatted_result = str(result)
    input_prompt = {"sql": sql, "result": formatted_result}
    human_response = generate_prompt | llm | StrOutputParser()
    answer = human_response.invoke(input_prompt)
    state["query_result"] = answer
    return state