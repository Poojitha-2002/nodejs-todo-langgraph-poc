from workflows.step3_graph import create_login_test_graph
import os

def main():
    spec_file_path = "/home/konduru.manasaveena/Desktop/nodejs-dashboard/nodejs-todo-langgraph-poc/spec_folder/avenio_spec.md"

    if not os.path.exists(spec_file_path):
        print(f"❌ Spec file not found at {spec_file_path}")
        return

    with open(spec_file_path, "r", encoding="utf-8") as f:
        spec_md = f.read()

    specific_url = "https://gpt.avenio.ai/chat"
    redirect_url = "http://127.0.0.1:8000/"

    step3_login_test_app = create_login_test_graph()
    inputs = {
        "spec_md": spec_md,
        "specific_url": specific_url,
        "email": os.getenv("Username"),
        "password": os.getenv("Password"),
        "redirect_url": redirect_url,
    }
    step3_result = step3_login_test_app.invoke(inputs)

    selenium_code_path = step3_result.get("selenium_code_path")
    if not selenium_code_path or not os.path.exists(selenium_code_path):
        print("❌ Selenium code not generated.")
        return

    # ✅ Add this to show test generation results
    test_status = step3_result.get("status")
    report_path = step3_result.get("test_report_path")
    error = step3_result.get("error")

    # print(
    #     f": Test report saved to {report_path}"
    #     if report_path
    #     else "❌ Report not generated"
    # )
    # print("Test Case Generation Status:", test_status)

    if error:
        print("Error:", error)


if __name__ == "__main__":
    main()
