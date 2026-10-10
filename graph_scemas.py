import requests
import time 

prev = None

def get_latest_issue():
    TOKEN = "YOUR TOKEN"
    REPO_OWNER = "kartik-lamkhade"
    REPO_NAME = "Random_Food_info"

    URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"

    HEADERS = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    params = {"state": "open", "sort": "created", "direction": "desc"}

    
    i = 0
    prev = []
    while True:

        response = requests.get(URL, headers=HEADERS, params=params)
        n  = response.json()[0]['number']

        if i == 0:
            a = 'old'
        else:
            a = 'new' if n != prev[-1] else 'old'
        i += 1
        prev.append(n)
        
        print ("no new issue found" if a == 'old' else "new issue found")
        time.sleep(5)
        prev = prev[-2:]
        if a == 'new':
            return {'new_issue': f"{a} is created no. is {prev}",'old_or_new':a}

if __name__ == "__main__":
    get_latest_issue()