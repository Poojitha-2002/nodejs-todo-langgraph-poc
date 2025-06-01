from workflows.step3_graph import create_login_test_graph
from workflows.step2_graph import create_spec_file_generation_graph
from nodes.test_case_generation import generate_test_case_with_report  # ✅ Import here
from schemas.state_schemas import AppState
import os

# def main():
#     github_repo_url = "https://github.com/Poojitha-2002/nodejs-todo-langgraph-poc/tree/master"

#     # Step 1: Generate spec
#     spec_graph = create_spec_file_generation_graph()
#     final_state = spec_graph.invoke({"github_url": github_repo_url})

#     print("\n✅ Step 1: Generated spec.md\n")
#     print(final_state["spec_md"])

#     with open("spec.md", "w", encoding="utf-8") as f:
#         f.write(final_state["spec_md"])

#     print("✅ spec.md has been saved successfully.\n")

#     # Step 2: Generate login code
#     step3_login_test_app = create_login_test_graph()
#     inputs = {
#         "login_spec": final_state["spec_md"],
#         "login_url": "http://127.0.0.1:4000/login",
#         "email": "manasakonduru11@gmail.com",
#         "password": "123456",
#     }
#     step3_result = step3_login_test_app.invoke(inputs)

#     selenium_code_path = step3_result.get("selenium_code_path")
#     if not selenium_code_path or not os.path.exists(selenium_code_path):
#         print("❌ Selenium code not generated.")
#         return

#     print("✅ Step 2: Selenium code generated:")
#     print(selenium_code_path)

#     # Step 3: Generate test case + report (call your function)
#     print("\n🚀 Step 3: Generating test case and report...\n")
#     state = AppState({
#         "selenium_code_path": selenium_code_path,
#         "login_url": "http://127.0.0.1:4000/login",
#         "email": "manasakonduru11@gmail.com",
#         "password": "123456",
#     })

#     result = generate_test_case_with_report(state)
#     print("\n📋 Final Result:\n", result)

# if __name__ == "__main__":
#     main()


def main():
    github_repo_url = (
        "https://github.com/Poojitha-2002/nodejs-todo-langgraph-poc/tree/master"
    )

    # Step 1: Generate spec
    spec_graph = create_spec_file_generation_graph()
    final_state = spec_graph.invoke({"github_url": github_repo_url})

    with open("spec.md", "w", encoding="utf-8") as f:
        f.write(final_state["spec_md"])

    print("✅ Generated spec.md and saved successfully.\n")

    # Step 2 + 3: Combined — generates Selenium + runs test + saves report
    step3_login_test_app = create_login_test_graph()
    inputs = {
        "login_spec": final_state["spec_md"],
        "login_url": "http://127.0.0.1:4000/login",
        "email": "manasakonduru11@gmail.com",
        "password": "123456",
    }
    step3_result = step3_login_test_app.invoke(inputs)

    selenium_code_path = step3_result.get("selenium_code_path")
    if not selenium_code_path or not os.path.exists(selenium_code_path):
        print("❌ Selenium code not generated.")
        return


if __name__ == "__main__":
    main()
