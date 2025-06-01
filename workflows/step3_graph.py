from langgraph.graph import StateGraph
from nodes.page_load_selenium import load_login_page
from schemas.state_schemas import AppState
from nodes.code_generation_selenium import generate_selenium_code
from nodes.test_case_generation import generate_test_case_with_report


def create_login_test_graph():
    graph = StateGraph(AppState)
    graph.add_node("load_page", load_login_page)
    graph.add_node("generate_code", generate_selenium_code)
    graph.add_node("generate_test_case_with_report", generate_test_case_with_report)
    graph.set_entry_point("load_page")
    graph.add_edge("load_page", "generate_code")
    graph.add_edge("generate_code", "generate_test_case_with_report")

    graph.add_conditional_edges(
        "generate_test_case_with_report",
        lambda state: (
            "end"
            if state.get("status") == "success"
            else ("generate_code" if state.get("retry_count", 0) < 3 else "end")
        ),
    )
    graph.set_finish_point("generate_test_case_with_report")

    return graph.compile()
