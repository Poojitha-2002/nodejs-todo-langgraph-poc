from workflows.step3_graph import create_login_test_graph
from workflows.step2_graph import create_spec_file_generation_graph

def main():
    
    github_repo_url = "https://github.com/Poojitha-2002/nodejs-todo-langgraph-poc/tree/master"
    
    # Compile and run the spec generation graph
    spec_graph = create_spec_file_generation_graph()
    final_state = spec_graph.invoke({"github_url": github_repo_url})

    print("\n✅ Step 1: Generated spec.md\n")
    print(final_state["spec_md"])

    with open("spec.md", "w", encoding="utf-8") as f:
        f.write(final_state["spec_md"])

    print("✅ spec.md has been saved successfully.\n")    
    
    step3_login_test_app = create_login_test_graph()
    inputs = {
        "login_spec": "Login form has 'username', 'password' fields and 'loginBtn' button.",
        "login_url" : "http://127.0.0.1:4000/login",
        "login_image": None,  # pass your image or placeholder
    }
    step2_result = step3_login_test_app.invoke(inputs)

    print("Step 2 completed: Selenium code generated:")
    print(step2_result.get("selenium_code"))


if __name__ == "__main__":
    main()
