from daytona import Daytona, DaytonaConfig
from langchain_ollama import ChatOllama
from daytona import Daytona, Sandbox
from typing import TypedDict,Annotated
import os
import time
from graph_scemas import get_latest_issue
from dotenv import load_dotenv

load_dotenv(r"C:\Users\karti\OneDrive\Documents\projects\github pr\.env")

model = ChatOllama(model="llama3.1:8b")


def runnable_loop(state):

    out = get_latest_issue()

    if out['old_or_new'] == 'new':
        return {'want_to_start_agent':'yes'}
    else:
        pass

    
def make_new_sandbox(state):
    api_key = os.getenv('daytona_api_key')
    config = DaytonaConfig(api_key=api_key)
    daytona = Daytona(config)
    sandbox = daytona.create()
    return {'sandbox':sandbox}

def pull_repo(state):
    repo_link = state['repo_link']
    sandbox = state['sandbox']
    github_token = state['github_token']
    repo_link_new = f"{repo_link[:8]}{github_token}@{repo_link[8:]}"
    try:
        out = sandbox.process.exec(f"git clone {repo_link_new}")
        repo_name = repo_link.split('/')[-1][:-4]
        files = sandbox.process.exec(f"cd {repo_name} && dir")
        file_list = [line.strip() for line in files.result.split('  ') if line.strip()]
        if out.exit_code == 0:
            return {'repo_pull':'true','repo_pull_content':out.result,'files_names_list':file_list,"repo_name":repo_name}
        else:
            return {'repo_pull':'flase','repo_pull_content':out.result,"repo_name":repo_name}
    except Exception as e:
        return {'repo_pull_content':out.result,"repo_name":repo_name}

def change_files_name_for_test(state):
    sandbox = state['sandbox']
    repo_name = state['repo_name']
    files_names_list = state['files_names_list']
    python_files = []
    for i in files_names_list:
        if i.endswith('.py'):
            python_files.append(i)

    # changing names for use pytest

    n = 1
    try:
        for file in python_files:
            sandbox.process.exec(f"cd {repo_name} && mv {file} test_{n}.py")
            n+=1
        files = sandbox.process.exec(f"cd {repo_name} && dir")
        file_list = [line.strip() for line in files.result.split('  ') if line.strip()]
        return {'change_files_name':"true",'files_names_list':file_list}
    except:
        return {'change_files_name':"false"}

def install_requirements(state):
    repo_name = state['repo_name']
    sandbox = state['sandbox']
    files_names_list = state['files_names_list']
    r_list = ['requirements.txt']
    n_list = [i.strip().lower() for i in files_names_list]
    if set(r_list) & set(n_list):
        matching_ele= list(set(r_list) & set(r_list))
        out = sandbox.process.exec(f"cd {repo_name} && pip install -r {matching_ele[0]}")
        if out.exit_code == 0:
            return {'install_requirements':'true','install_logs':out.result,'want_to_fix':'no','want_to_push': 'no'}
        else:
            return {'install_requirements':'false','install_logs':out.result,'want_to_fix':'no','want_to_push': 'no'}
    else:
        return {'install_requirements':'false','install_logs':'dosent have requirements files','want_to_fix':'no','want_to_push': 'no'}

def sample_code_run_test(state):
    sandbox = state['sandbox']
    repo_name = state['repo_name']
    sandbox.process.exec(
        "python -m pip install --upgrade "
        "opentelemetry-api==1.41.1 "
        "opentelemetry-sdk==1.41.1 "
        "opentelemetry-semantic-conventions==0.62b1"
    )
  
    try:
        output = sandbox.process.exec(f"cd {repo_name} && python -m pytest")

        return {'code_run_status':'successful' if output.exit_code in [0,5] else 'unsuccessful','code_running_logs':output.result,'fixing_code':'successful' if output.exit_code in [0,5] else 'unsuccessful','want_to_fix':'no' if output.exit_code in [0,5] and state['want_to_fix'] == 'no'  else 'yes','want_to_push': 'yes' if state['want_to_push'] == 'yes' else 'no'}
    except:
        return {'code_run_status':'unsuccessful','code_running_logs':output.result,'fixing_code':'unsuccessful','want_to_fix':'yes','want_to_push': 'no'}


def fix_code(state):
    sandbox = state['sandbox']
    repo_name = state['repo_name']
    if state['want_to_fix'] == 'yes':
        try:
            files_names_list = state['files_names_list']
            python_files = []
            for i in files_names_list:
                if i.endswith('.py'):
                    python_files.append(i)
            final_result = []
            for i in python_files:
                code = f"""with open('{repo_name}/{i}' , 'r') as f:
                file_content = f.read()
                print(file_content)"""
                file_content = sandbox.process.code_run(code)
                new_code = model.invoke(f"""
                        Fix the following Python code.

                        IMPORTANT:
                        - Return ONLY the complete corrected Python code.
                        - Do NOT write explanations.
                        - Do NOT write "Here's the corrected code".
                        - Do NOT use Markdown code fences such as ```python.
                        - The output must be directly executable Python code.

                        CODE:
                        {file_content.result}
                        """)
                code1 = f"""with open('{repo_name}/{i}' , 'w') as f:
                f.write({new_code.content!r})"""
                output = sandbox.process.code_run(code1)
                final_result.append({'output':output,'exit_code':output.exit_code,'file_name':i})
            exit_codes = [i['exit_code'] for i in final_result]
            is_success = all(code in [0, 5] for code in exit_codes)
            print(is_success)
            return {'fixing_code': 'successful' if is_success else 'unsuccessful','fixing_code_logs':f"this files is not fixing {[i['file_name'] for i in final_result if i['exit_code'] in [0,5]]} if no all files are good",'want_to_push':'yes','want_to_fix':'no'}
        except Exception as e:
            return {'fixing_code': 'unsuccessful','fixing_code_logs':f'code broke : {e}','want_to_push':'yes','want_to_fix':'no'}
    else:
        return {'fixing_code_logs':'Not need','want_to_push':'no','want_to_fix':'no'}


def push_all_code(state):
    if state['want_to_push'] == 'yes':
        repo_link = state['repo_link']
        sandbox = state['sandbox']
        github_token = state['github_token'].strip()                   
        remote = f"{repo_link[:8]}x-access-token:{github_token}@{repo_link[8:]}"
        repo_name = state['repo_name']
        logs = []
        branch = f"fixing_problem_{int(time.time())}" 
        def run(cmd):
            return sandbox.process.exec(f"cd {repo_name} && {cmd}")
        o = run("git config user.name 'kartik-lamkhade'")
        logs.append(o)
        o = run("git config user.email 'kartik-lamkhade@users.noreply.github.com'")
        logs.append(o)
        o = run(f"git remote set-url origin {remote}")
        logs.append(o)
        o = sandbox.process.exec(f"cd {repo_name} && git checkout -b {branch}")
        logs.append(o)
        o = sandbox.process.exec(f"cd {repo_name} && git add .")
        logs.append(o)
        o = sandbox.process.exec(f"cd {repo_name} && git commit -m 'fix_code'")
        logs.append(o)
        o =  sandbox.process.exec(f"cd {repo_name} && git push -u --force-with-lease origin {branch}")
        logs.append(o)
        return {'git_push_status': 'successful' if logs[-1].exit_code in [0, 5] else 'unsuccessful','git_push_logs':logs}
    return {'git_push_logs':'not need'}
 
def delet_sandbox(state):
    sandbox = state['sandbox']
    try:
        sandbox.delete()
        return {'delet_sandbox':'successful'}
    except Exception as e:
        return {'delet_sandbox':'unsuccessful'}