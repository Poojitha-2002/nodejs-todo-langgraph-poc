from langgraph.graph import StateGraph
from nodes.page_load_selenium import load_page
from nodes.code_generation_selenium import generate_selenium_code
from nodes.reflection_code_generation import reflection_on_code_gen
from nodes.test_case_generation import generate_test_case_with_report
from nodes.reflection_node import reflect_and_correct_test_case
from schemas.state_schemas import AppState
import logging
def create_login_test_graph():
    graph = StateGraph(AppState)
    graph.add_node("load_page", load_page)
    graph.add_node("generate_selenium_code", generate_selenium_code)
    graph.add_node("selenium_reflect_code", reflection_on_code_gen)
    graph.add_node("generate_test_case_with_report", generate_test_case_with_report)
    graph.add_node("testcase_reflect_code", reflect_and_correct_test_case)
    graph.set_entry_point("load_page")
    graph.add_edge("load_page", "generate_selenium_code")
    graph.add_edge("generate_selenium_code", "selenium_reflect_code")
    # graph.add_edge("generate_selenium_code", "generate_test_case_with_report")
    graph.add_conditional_edges(
        "selenium_reflect_code",
        lambda state: (
            "reflect" if state.get("should_reflect", False) else "generate_test"
        ),
        {
            "reflect": "generate_selenium_code",
            "generate_test": "generate_test_case_with_report",
        },
    )
    # graph.add_edge("selenium_reflect_code", "generate_selenium_code")
    # graph.add_edge("selenium_reflect_code", "generate_test_case_with_report")
    graph.add_conditional_edges(
        "generate_test_case_with_report",
        lambda state: (
            "end"
            if state.get("status") == "success"
            else ("correct_code" if state.get("retry_count", 0) < 3 else "end")
        ),
        {"end": "__end__", "correct_code": "testcase_reflect_code"},
    )
    graph.add_edge("testcase_reflect_code", "generate_test_case_with_report")
    graph.set_finish_point("generate_test_case_with_report")
    app = graph.compile()
    mermaid_code = app.get_graph().draw_mermaid_png()
    with open("test_case_generation.png", "wb") as f:
        f.write(mermaid_code)

    return app