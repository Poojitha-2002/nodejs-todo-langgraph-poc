from typing import TypedDict, Optional

class AppState(TypedDict):
    login_spec: str
    login_url: str
    page_html: str
    selenium_code_path: str
    image_path: Optional[str]
    driver_path: Optional[str]
    retry_count: Optional[int]