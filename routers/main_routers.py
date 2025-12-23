from state.agent_state import *

# Routing functions
def relevance_router(state: AgentState):
    return "convert_to_sql" if state["relevance"].lower() == "relevant" else "generate_funny_response"

def execute_sql_router(state: AgentState):
    return "generate_human_readable_answer" if not state.get("sql_error", False) else "regenerate_query"

def check_attempts_router(state: AgentState):
    return "convert_to_sql" if state["attempts"] < 3 else "end_max_iterations"