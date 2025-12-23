from state.agent_state import *
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os 
from langchain_openai import ChatOpenAI
from env.api_key import *


# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0.5)

def generate_funny_response(state: AgentState):
    system = """You are a charming and funny assistant who responds in a playful manner."""
    human_message = "I can not help with that, but doesn't asking questions make you come closer to the problem? You can always revise the data."
    funny_prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human_message)])
    funny_response = funny_prompt | llm | StrOutputParser()
    message = funny_response.invoke({})
    state["query_result"] = message
    return state

def regenerate_query(state: AgentState):
    question = state["question"]
    system = """You are an assistant that reformulates an original question to enable more precise SQL queries."""
    rewrite_prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", f"Original Question: {question}\nReformulate the question to enable more precise SQL queries.")
    ])
    rewriter = rewrite_prompt | llm | StrOutputParser()
    rewritten = rewriter.invoke({})
    state["question"] = rewritten
    state["attempts"] += 1
    return state

def end_max_iterations(state: AgentState):
    state["query_result"] = "Please try again."
    return state