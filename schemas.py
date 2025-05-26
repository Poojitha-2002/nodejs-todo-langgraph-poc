from typing import TypedDict

class AppState(TypedDict):
    login_spec: str
    login_url: str
    page_html: str
    selenium_code: str