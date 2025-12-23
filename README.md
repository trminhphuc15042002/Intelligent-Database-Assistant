# Intelligent Database Assistant

## 📌 Overview
Intelligent Database Assistant is a Streamlit-based application that allows users to interactively query and analyze relational databases using an AI-powered agent.  
The system connects to SQL databases, processes user queries, and generates insights and visualizations in a user-friendly interface.

---

## 🚀 Features
- Connect to relational databases (PostgreSQL, MySQL)
- AI-powered database query and analysis agent
- Interactive data exploration and visualization
- Modular and extensible agent-based architecture
- User-friendly Streamlit web interface

---

## 🛠 Tech Stack
- **Python**
- **Streamlit**
- **SQLAlchemy**
- **OpenAI API**
- **Pandas / Matplotlib**
- **PostgreSQL / MySQL**

---

## 📂 Project Structure
```text
database_agent_ui/
├── graph/                     # Agent workflow and graph logic
├── routers/                   # Application routing logic
├── state/                     # Agent state management
├── tools/                     # Database and visualization tools
├── database_query_agent_ui.py # Main Streamlit application
├── requirement.txt            # Project dependencies
└── .gitignore                 # Git ignore configuration
```

---
## 🧠 Agent Workflow
The diagram below illustrates the agent-based workflow used to process user queries, validate relevance, generate SQL queries, execute them, and produce human-readable insights.
<img width="800" height="814" alt="image" src="https://github.com/user-attachments/assets/df1faf72-3acc-4780-8720-1ebae5197025" />


## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2.Create and activate a virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate   # On Windows: myenv\Scripts\activate
```

### 3.Install dependencies:
```bash
pip install -r requirement.txt
```

## 🔐 Environment Variables
```bash
Create a .env file in the project root and add:
OPENAI_API_KEY=your_openai_api_key
```
## Create a virtual Python environment:
```bash
python -m venv myenv
```
Active
```bash
.\myenv\Scripts\activate
```
## ▶️ Usage
Run the Streamlit application:
```bash
python -m streamlit run database_query_agent_ui.py
```
Then open your browser at:
```bash
http://localhost:8501
```
<img width="2557" height="1394" alt="image" src="https://github.com/user-attachments/assets/ea262c7f-6677-46fd-b45e-a52c6c236b90" />

## 📈 Future Improvements
- **Support for additional database engines**
- **Advanced query optimization**
- **Enhanced data visualization options**
- **User authentication and access control**

## 🧩 Code
Import
```bash
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float # Import các package để chạy ra được schema db
from sqlalchemy.orm import sessionmaker, relationship, declarative_base # Để khởi tạo session thực thi SQL query dưới RDBMS
# Khởi tạo Agent State
from langchain_core.runnables.config import RunnableConfig
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI # Dùng LLM từ OpenAI
from langchain_core.prompts import ChatPromptTemplate # Thiết lập system prompt để LLM hiểu rõ nhiệm vụ của mình
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy import text,inspect # Chuẩn hóa SQL query trước khi thực thi query dưới RDBMS
from langgraph.graph import StateGraph, END #Nối các Agent Node lại thành Agent Graph hoàn chỉnh
```
DB params:
```text
Host: 112.213.86.31
Port: 3360 
Username: marshmallow
Password: N3unkNbXQYh33og
Database: carbon_emissions
```
```bash
db_params = {
    "host": "112.213.86.31",
    "port": 3360,
    "username": "marshmallow",
    "password": "N3unkNbXQYh33og",
    "database": "carbon_emissions"
}

DATABASE_URL = f"mysql+pymysql://{db_params["username"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["database"]}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

```bash
OPENAI_API_KEY=your_openai_api_key
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_key, temperature=0.5)
```
```bash
# Input: engine
# Output: string chứa hết tất cả các cột từ các bảng trong RBDMS (Data Warehouse) và cách các table liên lạc với nhau

def get_database_schema(engine):
    inspector = inspect(engine)
    schema = ""

    for table_name in inspector.get_table_names():
        schema += f"Table: {table_name}\n"
        for column in inspector.get_columns(table_name):
            col_name = column["name"]
            col_type = column["type"]
            if column.get("primary_key"):
                col_type += ", Primary Key"
            if column.get("foreign_key"):
                foreign_key = list(column["foreign_keys"])[0]
                col_type += f", Foreign Key to {foreign_key.table.name}.{foreign_key.column.name}"
            schema += f"- {col_name}: {col_type}\n"
        schema += "\n"
    print("Hoàn tất việc thu thập database schema")
    return schema
```
```bash
database_schema = get_database_schema(engine)
database_schema
```

### 1.Khởi tạo Agent State
```bash
class AgentState(TypedDict):
  question: str
  sql_query: str
  query_result: str
  query_rows: list
  attempts: int
  relevance: str
  sql_error: bool
```
### 2.Khởi tạo các tool
#### 2.1 Tool Check Relevance
```bash
class CheckRelevance(BaseModel):
    relevance: str = Field(
        description="Indicates whether the question is related to the database schema. 'relevant' or 'not_relevant'."
    )

def check_relevance(state: AgentState, config: RunnableConfig):
    question = state["question"]
    schema = get_database_schema(engine)
    print(f"Kiểm tra xem câu hỏi của user có phù hợp hay không: {question}")

    system = """You are an assistant that determines whether a given question is related to the following database schema.

Schema:
{schema}

Respond with only "relevant" or "not_relevant".
""".format(schema=schema)

    human = f"Question: {question}"
    check_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", human)
        ]
    )

    structured_llm = llm.with_structured_output(CheckRelevance)
    relevance_checker = check_prompt | structured_llm
    relevance = relevance_checker.invoke({})

    state["relevance"] = relevance.relevance
    print(f"Relevance determined: {state["relevance"]}")
    return state
```
```bash
def generate_funny_response(state: AgentState):
    print("Câu hỏi không liên quan")
    system = """You are a charming and funny assistant who responds in a playful manner.
    """
    human_message = "I can not help with that, but doesn't asking questions make you come closer to the problem? You can always revise the data."

    response_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", human_message)
        ]
    )

    response = response_prompt | llm | StrOutputParser()
    message = response.invoke({})
    state["query_result"] = message
    return state
```
#### 2.2 Tool convert text to SQL
```bash
class ConvertToSQL(BaseModel):
    sql_query: str = Field(
        description="The SQL query corresponding to the user's natural language question."
    )

def convert_to_sql(state: AgentState, config: RunnableConfig):
    question = state["question"]

    schema = get_database_schema(engine)
    system = """You are an assistant that converts natural language questions into SQL queries based on the following schema:

{schema}

The current question is '{question}'. Ensure that all query-related data is scoped to this question.

Provide only the SQL query without any explanations. Alias columns appropriately to match the expected keys in the result.

For example, alias 'food.name' as 'food_name' and 'food.price' as 'price'.
""".format(schema=schema, question=question)

    convert_prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Question: {question}")
    ])

    structured_llm = llm.with_structured_output(ConvertToSQL)
    sql_generator = convert_prompt | structured_llm
    result = sql_generator.invoke({"question": question})
    state["sql_query"] = result.sql_query
    print(f"Câu SQL query đã được tạo ra: {state["sql_query"]}")
    return state
```
#### 2.3 Tool thực thi SQL query
```bash
def execute_sql(state: AgentState):
  sql_query = state["sql_query"].strip()
  session = SessionLocal()
  print(f"Thực thi lệnh SQL: {sql_query}")

  try:
    result = session.execute(text(sql_query))
    if sql_query.lower().startswith("select"):
      rows = result.fetall()
      colomns = result.keys()
      if rows:
        state["query_rows"] = [dict(zip(columns,row)) for row in rows]
        query_result = f"Tìm thấy {len(state["query_rows"])}"
      else:
        state["query_rows"] = {}
        query_result = "Không có dữ liệu"
      state["query_result"] = query_result
      state["sql_error"] = False
    else:
      session.commit()
      state["query_result"] = "Hoàn tất việc thực thi câu query"
      state["sql_error"] = False
  except Exception as e:
    state["query_result"] = f"Lỗi trong lúc thực thi query: {str(e)}"
    state["sql_error"] = True
  finally:
    session.close()
  return state
```
```bash
def relevance_router(state: AgentState):
  if state["relevance"].lower() == "relevant":
    return "convert_to_sql"
  else:
    return "generate_funny_response"
```
```bash
class RewrittenQuestion(BaseModel):
  question: str = Field(description="The rewritten question.")

def regenerate_query(state: AgentState):
    question = state["question"]
    print("Đang tạo lại truy vấn")

    system = """You are an assistant that reformulates an original question to enable more precise SQL queries. Ensure that all necessary details, such as table joins, are preserved to retrieve complete and accurate data.
    """

    rewrite_prompt = ChatPromptTemplate.from_messages([
        ("system",system),
        (
            "human",
            f"Original Question: {question}\nReformulate the question to enable more precise SQL queries, ensuring all necessary details are preserved."
        )
    ])
    structured_llm = llm.with_structured_output(RewrittenQuestion)
    rewriter = rewrite_prompt | structured_llm
    rewritten = rewriter.invoke({})
    state["question"] = rewritten.question
    state["attempts"] += 1
    print(f"Truy vấn được tạo lại cho câu hỏi: {state["question"]}")
    return state
```
```bash
def end_max_iterations(state: AgentState):
  state["query_result"] = "Please try again"
  print("Số lần lặp lại truy vấn đã đến mức tối đa")
  return state
```
```bash
def check_attempts_router(state: AgentState):
    if state["attempts"] < 3:
        return "convert_to_sql"
    else:
        return "max_iterations"
```
```bash
def execute_sql_router(state: AgentState):
  if not state.get("sql_error",False):
    return "generate_human_readable_answer"
  else:
    return "regenerate_query"
```
#### 2.4 Generate human Readable Answer
```bash
def generate_human_readable_answer(state: AgentState):
    sql = state["sql_query"]
    result = state.get("query_rows", [])
    sql_error = state.get("sql_error", False)

    print("Đang trả về insight từ data")

    system = """You are an assistant that converts SQL query results into clear, natural language responses without including any identifiers like IDs."""

    if sql_error:
        generate_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", """SQL Query:\n{sql}\nResult:\n{result}\nFormulate a clear and understandable error message in a single sentence.""")
            ]
        )

    elif sql.lower().startswith("select"):
        generate_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", """SQL Query:\n{sql}\nResult:\n{result}\nFormulate a clear and understandable answer to the original question in detail.""")
            ]
        )
    else:
        generate_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", """SQL Query:\n{sql}\nResult:\n{result}\nFormulate a clear and understandable confirmation message in detail.""")
            ]
        )

    formatted_result = str(result)

    input_prompt = {
        "sql": sql,
        "result": formatted_result
    }

    human_response = generate_prompt | llm | StrOutputParser()

    answer = human_response.invoke(input_prompt)

    state["query_result"] = answer

    print("Hoàn tất luồng chạy phân tích dữ liệu tự động")
    return state
```
### 3.Thiết lập các Agent Node
```bash
workflow = StateGraph(AgentState)
```
```bash
workflow.add_node("check_relevance", check_relevance)
workflow.add_node("generate_funny_response", generate_funny_response)
workflow.add_node("convert_to_sql", convert_to_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("regenerate_query", regenerate_query)
workflow.add_node("end_max_iterations", end_max_iterations)
workflow.add_node("generate_human_readable_answer", generate_human_readable_answer)
```
### 4.Thiết lập Agent Graph
```bash
workflow.add_conditional_edges(
    "check_relevance",
    relevance_router,
    {
        "convert_to_sql": "convert_to_sql",
        "generate_funny_response": "generate_funny_response"
    }
)

workflow.add_edge("convert_to_sql", "execute_sql")

workflow.add_conditional_edges(
    "execute_sql",
    execute_sql_router,
    {
        "generate_human_readable_answer": "generate_human_readable_answer",
        "regenerate_query": "regenerate_query"
    }
)

workflow.add_conditional_edges(
    "regenerate_query",
    check_attempts_router,
    {
        "convert_to_sql": "convert_to_sql",
        "max_iterations": "end_max_iterations"
    }
)

workflow.add_edge("generate_human_readable_answer", END)
workflow.add_edge("generate_funny_response", END)
workflow.add_edge("end_max_iterations", END)

workflow.set_entry_point("check_relevance")

app = workflow.compile()
```
#### Test
```bash
user_question = "What are the companies with the highest contribution to carbon emissions?"
result = app.invoke({"question": user_question,"attempts":0})
print(f"Kết quả: {result}")
```
```bash
Kết quả: {'question': 'Which companies have the highest total carbon emissions contribution in a specific year, considering the emissions data from a table that includes company names, carbon emissions, and the year the emissions were recorded?', 'sql_query': 'SELECT c.company_name AS company_name, SUM(pe.carbon_footprint_pcf) AS total_carbon_emissions \nFROM product_emissions pe \nJOIN companies c ON pe.company_id = c.id \nWHERE pe.year = :specific_year \nGROUP BY c.company_name \nORDER BY total_carbon_emissions DESC \nLIMIT 1', 'query_result': 'Please try again', 'attempts': 3, 'relevance': 'relevant', 'sql_error': True}
```
