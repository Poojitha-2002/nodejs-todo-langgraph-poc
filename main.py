from workflows.step3_graph import create_login_test_graph
from workflows.step2_graph import create_spec_file_generation_graph
from nodes.test_case_generation import generate_test_case_with_report  # ✅ Import here
from nodes.state_schemas import AppState
import os

def main():
    github_repo_url = "https://github.com/Poojitha-2002/nodejs-todo-langgraph-poc/tree/master"

    # Step 1: Generate spec
    spec_graph = create_spec_file_generation_graph()
    final_state = spec_graph.invoke({"github_url": github_repo_url})

    print("\n✅ Step 1: Generated spec.md\n")
    print(final_state["spec_md"])

    with open("spec.md", "w", encoding="utf-8") as f:
        f.write(final_state["spec_md"])

    print("✅ spec.md has been saved successfully.\n")

    # Step 2: Generate login code
    step3_login_test_app = create_login_test_graph()
    inputs = {
        "login_spec": final_state["spec_md"],
        "login_url": "http://127.0.0.1:4000/login",
    }
    step3_result = step3_login_test_app.invoke(inputs)

    selenium_code = step3_result.get("selenium_code")
    if not selenium_code:
        print("❌ Selenium code not generated.")
        return

    print("✅ Step 2: Selenium code generated:")
    print(selenium_code)

    # Step 3: Generate test case + report (call your function)
    print("\n🚀 Step 3: Generating test case and report...\n")
    state = AppState({
        "selenium_code": selenium_code,
        "login_url": "http://127.0.0.1:4000/login",
        "email": "manasakonduru11@gmail.com",
        "password": "123456",
    })

    result = generate_test_case_with_report(state)
    print("\n📋 Final Result:\n", result)

if __name__ == "__main__":
    main()
