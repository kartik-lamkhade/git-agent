import os
from graph_state import graph_state
from daytona import Daytona, DaytonaConfig
from langchain_ollama import ChatOllama
from daytona import Daytona, Sandbox
from typing import TypedDict,Annotated,Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,END
from langchain_ollama import ChatOllama
from graph_nodes import make_new_sandbox,pull_repo,change_files_name_for_test,sample_code_run_test,install_requirements,fix_code,push_all_code,delet_sandbox,runnable_loop

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "YOUR TOKEN"
os.environ["LANGCHAIN_API_KEY"] = "YOUR TOKEN"
os.environ["LANGCHAIN_PROJECT"] = "git_issue_solve"


load_dotenv(r"C:\Users\karti\OneDrive\Documents\projects\github pr\.env")

model = ChatOllama(model="llama3.1:8b")

graph = StateGraph(graph_state)

def condition(state)-> Literal["fix_code", "push_all_code", "delet_sandbox"]:
    status = state.get('fixing_code')
    status_1 = state.get('want_to_fix')
    status_2 = state.get('want_to_push')
    if status_1 == 'no' and status_2 == 'no':
        return 'delet_sandbox'
    else:
        return "push_all_code" if status == 'successful' else 'fix_code'

graph.add_node('make_new_sandbox',make_new_sandbox)
graph.add_node('pull_repo',pull_repo)
graph.add_node('fix_code',fix_code)
graph.add_node('change_files_name_for_test',change_files_name_for_test)
graph.add_node('sample_code_run_test',sample_code_run_test)
graph.add_node('install_requirements',install_requirements)
graph.add_node('push_all_code',push_all_code)
graph.add_node('delet_sandbox',delet_sandbox)
graph.add_node('runnable_loop',runnable_loop)

graph.add_edge(START,'runnable_loop')
graph.add_edge('runnable_loop','make_new_sandbox')
graph.add_edge('make_new_sandbox','pull_repo')
graph.add_edge('pull_repo','change_files_name_for_test')
graph.add_edge('change_files_name_for_test','install_requirements')
graph.add_edge('install_requirements','sample_code_run_test')
graph.add_conditional_edges('sample_code_run_test',condition)

graph.add_edge('fix_code','sample_code_run_test')
graph.add_edge('push_all_code','delet_sandbox')
graph.add_edge('delet_sandbox','runnable_loop')

workflow = graph.compile()

output = workflow.invoke({'repo_link':"PUT YOUR REPO LINK","github_token":"GITHUB TOKEN"})

print(output)

