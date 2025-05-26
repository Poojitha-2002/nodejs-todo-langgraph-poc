from workflows.step2_graph import create_login_test_graph


def main():

    step2_app = create_login_test_graph()
    inputs = {
        "login_spec": "Login form has 'username', 'password' fields and 'loginBtn' button.",
        "login_url" : "http://127.0.0.1:4000/login",
        "login_image": None,  # pass your image or placeholder
    }
    step2_result = step2_app.invoke(inputs)

    print("Step 2 completed: Selenium code generated:")
    print(step2_result.get("selenium_code"))


if __name__ == "__main__":
    main()
