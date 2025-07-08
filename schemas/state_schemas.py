from typing import TypedDict, Optional, Annotated
from langgraph.graph import add_messages


class AppState(TypedDict):
    github_url: str
    readme: str
    login_context: str
    spec_md: str
    # login_spec: str
    url: str
    page_html: str
    selenium_code_path: str
    image_path: Optional[str]
    driver_path: Optional[str]
    test_case_path: Optional[str]
    retry_count: Optional[int]
    email: Optional[str]
    password : Optional[str]
    error: Optional[str]
    status: Optional[str]
    home_page_url: Optional[str]
    messages: Annotated[list, add_messages]
    reflect_loop_count: int = 0

class ReflectionState(AppState):
    should_reflect: bool
    
