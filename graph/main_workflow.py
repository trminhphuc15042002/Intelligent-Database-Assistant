from langgraph.graph import StateGraph, END
from tools.agent_tools import *
from tools.sub_tools import * 
from routers.main_routers import *
from state.agent_state import *


# Workflow setup
workflow = StateGraph(AgentState)
workflow.add_node("check_relevance", check_relevance)
workflow.add_node("convert_to_sql", convert_nl_to_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("generate_human_readable_answer", generate_human_readable_answer)
workflow.add_node("generate_funny_response", generate_funny_response)
workflow.add_node("regenerate_query", regenerate_query)
workflow.add_node("end_max_iterations", end_max_iterations)

workflow.add_conditional_edges("check_relevance", relevance_router, {
    "convert_to_sql": "convert_to_sql",
    "generate_funny_response": "generate_funny_response"
})
workflow.add_edge("convert_to_sql", "execute_sql")
workflow.add_conditional_edges("execute_sql", execute_sql_router, {
    "generate_human_readable_answer": "generate_human_readable_answer",
    "regenerate_query": "regenerate_query"
})
workflow.add_conditional_edges("regenerate_query", check_attempts_router, {
    "convert_to_sql": "convert_to_sql",
    "end_max_iterations": "end_max_iterations"
})
workflow.add_edge("generate_human_readable_answer", END)
workflow.add_edge("generate_funny_response", END)
workflow.add_edge("end_max_iterations", END)
workflow.set_entry_point("check_relevance")

# Compile graph
app = workflow.compile()