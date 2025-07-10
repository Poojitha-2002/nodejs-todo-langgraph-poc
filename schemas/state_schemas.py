from typing import TypedDict, Optional, Annotated
from langgraph.graph import add_messages
from selenium.webdriver.chrome.webdriver import WebDriver


class AppState(TypedDict):
    github_url: str
    readme: str
    login_context: str
    spec_md: str
    login_spec: str
    specific_url: str
    page_html: str
    selenium_code_path: str
    test_file_path: str
    test_report_path: str
    image_path: Optional[str]
    driver_path: Optional[WebDriver]
    retry_count: Optional[int]
    email: Optional[str]
    password : Optional[str]
    error: Optional[str]
    status: Optional[str]
    redirect_url: Optional[str]
    messages: Annotated[list, add_messages]
    reflect_loop_count: int = 0
    authentication_required: Optional[bool]

class ReflectionState(AppState):
    should_reflect: bool
