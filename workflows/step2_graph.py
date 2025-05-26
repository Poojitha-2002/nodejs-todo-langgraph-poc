from langgraph.graph import StateGraph, END
from nodes.Spec_file_generation import fetch_readme, extract_login_info, generate_spec
from nodes.Spec_file_generation import AppState

def create_spec_file_generation_graph():
    graph = StateGraph(AppState)
    graph.add_node("FetchReadme", fetch_readme)
    graph.add_node("ExtractLoginInfo", extract_login_info)
    graph.add_node("GenerateSpec", generate_spec)

    graph.set_entry_point("FetchReadme")
    graph.add_edge("FetchReadme", "ExtractLoginInfo")
    graph.add_edge("ExtractLoginInfo", "GenerateSpec")
    graph.set_finish_point("GenerateSpec")

    app = graph.compile()
    return app

   