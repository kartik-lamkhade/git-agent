from typing import TypedDict,Literal
from daytona import Daytona, Sandbox
from typing import TypedDict,Annotated,List


def skip_serialization(left: Sandbox | None, right: Sandbox | None) -> Sandbox | None:
    return right if right is not None else left

class graph_state(TypedDict):
    new_issue: Literal['yes','no']
    repo_pull: Literal['true','false']
    code_run_status: Literal['successful','unsuccessful']
    create_new_sandbox: Literal['successful','unsuccessful']
    new_code: str
    files_names_list : List[str]
    repo_link: str
    want_to_merge: Literal['yes','no']
    sandbox: Annotated[Sandbox | None, skip_serialization] 
    repo_pull_content: str
    repo_name: str
    change_files_name: Literal['true','false']
    code_running_logs: str
    install_requirements: Literal['true','false']
    install_logs: str
    fixing_code: Literal['successful','unsuccessful']
    fixing_code_logs: str
    github_token: str
    git_push_status: Literal['successful','unsuccessful']
    git_push_logs: str
    delet_sandbox: Literal['successful','unsuccessful']
    want_to_push: Literal['yes','no']
    want_to_fix: Literal['yes','no']
    want_to_start_agent: Literal['yes','no']
