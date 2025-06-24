import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from schemas.state_schemas import ReflectionState
import logging

def reflection_on_code_gen(state: ReflectionState):
    code_critique = '''
    ### ROLE
    You are an intelligent QA engineer who is skilled at reading, reviewing and crafting efficient testcases. You will be given a selenium code which is to test some functional specifications of a page. Your task is to go through the code, understand it and see if the code is upto the mark. 

    ### INSTRUCTIONS
    See to the fact that the code given is good enough to be sent to the next node. If you find there was a mistake in the generated code, come up with constructive criticism for the code to improve. If you think the code is syntactically correct and has been produced based on the given context, then consider yourself satisfied.
    If the code is satisfactory and it can pass onto the next node, then return STOP and nothing else. Just STOP, no nextline, no spaces, no special characters, just STOP.

    Here's the selenium code:
'''

    if state.get("reflect_loop_count", 0) <= 3:
        prompt = ChatPromptTemplate.from_messages([
            ('system', code_critique),
            ('human', "{input}"),
            MessagesPlaceholder("messages"),
        ])

        gemini_api_key = os.getenv("GEMINI_API_KEY")

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

        chain = prompt | llm | StrOutputParser()

        latest_code = state["messages"][-1].content if state.get("messages") else ""

        response = chain.invoke({
            "input": latest_code,
            "messages": state["messages"]
        })

        if response == "STOP":
            logging.info("Code satisfied. Moving onto generating testcases and reports.")
            state["should_reflect"] = False
        else:
            logging.info("Code unsatisfied. Reflecting graph to itself for improvements.")
            state["should_reflect"] = True
            state["reflect_loop_count"] = state.get("reflect_loop_count", 0) + 1
            state["messages"] = state.get("messages", []) + [HumanMessage(content=response)]
    else:
        logging.info("Reflection loop count exceeded. Proceeding without further reflection.")
        state["should_reflect"] = False

    return state


# from dotenv import load_dotenv
# load_dotenv()
# code_snippet = '''
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

# def login(url, username, password, home_page_element_locator): #Changed parameter
#     driver = webdriver.Chrome()
#     driver.get("https://" + url) #Corrected protocol
#     try:
#         email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email"))) #Example locator, adjust as needed
#         password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))) #Example locator, adjust as needed
#         login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submitLogin"))) #Example locator, adjust as needed

#         email_field.send_keys(username)
#         password_field.send_keys(password)
#         login_button.click()

#         WebDriverWait(driver, 10).until(EC.presence_of_element_located(home_page_element_locator)) #Check for homepage element

#     except TimeoutException as e:
#         print(f"Timeout happened: {e}")
#     finally:
#         driver.quit()
# '''

# gemini_api_key = os.getenv("GEMINI_API_KEY")

# llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2, api_key=gemini_api_key)

# def try_reflection_functionality(code, llm):
#     prompt = '''### ROLE
#     You are an intelligent QA engineer who is skilled at reading, reviewing and crafting efficient testcases. You will be given a selenium code which is to test some functional specifications of a page. Your task is to go through the code, understand it and see if the code is upto the mark. 

#     ### INSTRUCTIONS
#     See to the fact that the code given is good enough to be sent to the next node. If you find there was a mistake in the generated code, come up with constructive criticism for the code to improve. 
#     If the code is satisfactory and it can pass onto the next node, then return STOP and nothing else. Just STOP, no nextline, no spaces, no special characters, just STOP.

#     Here's the selenium code:'''

#     prompt_reflection = ChatPromptTemplate.from_messages([
#             ('system', prompt),
#             ('human', "{input}")
#         ])

#     chain = prompt_reflection | llm | StrOutputParser()

#     response = chain.invoke({"input": code})
    
#     return response


# print(try_reflection_functionality(code_snippet,llm))