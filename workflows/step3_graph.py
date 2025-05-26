from langgraph.graph import StateGraph
from nodes.page_load_selenium import load_login_page
from schemas import AppState
from nodes.code_generation_selenium import generate_selenium_code

def create_login_test_graph():
    graph = StateGraph(AppState)
    graph.add_node("load_page", load_login_page)
    graph.add_node("generate_code", generate_selenium_code)

    graph.set_entry_point("load_page")
    graph.add_edge("load_page", "generate_code")
    graph.set_finish_point("generate_code")

    return graph.compile()
