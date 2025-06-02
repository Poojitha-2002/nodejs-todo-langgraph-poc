from typing import TypedDict, Optional


class AppState(TypedDict):
    github_url: str
    readme: str
    login_context: str
    spec_md: str
    login_spec: str
    login_url: str
    page_html: str
    selenium_code_path: str
    image_path: Optional[str]
    driver_path: Optional[str]
    retry_count: Optional[int]
    email: Optional[str]
    password : Optional[str]
    error: Optional[str]
