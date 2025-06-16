from workflows.step3_graph import create_login_test_graph
from workflows.step2_graph import create_spec_file_generation_graph
from nodes.test_case_generation import generate_test_case_with_report 
from schemas.state_schemas import AppState
import os

def main():
    spec_file_path = "spec_folder/spec.md"

    if not os.path.exists(spec_file_path):
        print(f"❌ Spec file not found at {spec_file_path}")
        return

    with open(spec_file_path, "r", encoding="utf-8") as f:
        spec_md = f.read()

    # Step 2 + 3: Combined — generates Selenium + runs test + saves report
    step3_login_test_app = create_login_test_graph()
    inputs = {
        "login_spec": spec_md,
        "login_url": "http://127.0.0.1:4000/login",
        "email": os.getenv("EMAIL"),
        "password": os.getenv("PASSWORD"),
        "home_page_url": "http://127.0.0.1:4000/dashboard",
    }
    step3_result = step3_login_test_app.invoke(inputs)

    selenium_code_path = step3_result.get("selenium_code_path")
    if not selenium_code_path or not os.path.exists(selenium_code_path):
        print("❌ Selenium code not generated.")
        return


if __name__ == "__main__":
    main()
