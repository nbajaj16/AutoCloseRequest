import os
import requests
import yaml
import pandas as pd

from datetime import datetime, timedelta, timezone

temp_dict = {}

with open("config.yml") as file:
    try:
        pr_data = yaml.safe_load(file)
        for key, value in pr_data.items():
            temp_dict["url"] = value[0]["url"]
            temp_dict["names"] = value[0]["notify_to"]
    except yaml.YAMLError as exception:
        print(exception)

repo_url = temp_dict['url']

repo_owner, repo_name = repo_url.split(os.path.sep)[-2:]

#apis
api_pulls = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
api_for_email = f"https://api.github.com/users/{repo_owner}/events/public"
access_token = os.environ("access_token")

def get_data(api):
    response = requests.get(api)
    return response.json()

pull_requests = get_data(api_pulls)

def email_func():
    print("Sending a slack message to:")
    for name in temp_dict["names"].split(", "):
        print(name)
    print("\n")

def close_request(number):
    patch_api = f"{api_pulls}/{number}"
    data = {
        'state' : 'closed'
    } 
    headers = {
        "Authorization" : f"Bearer {access_token}"
    }
    patch_request = requests.patch(patch_api, headers=headers, json=data)
    return patch_request

for pr_data in pull_requests:
    if pr_data['state'] == 'open' and pr_data['base']['ref'] == 'b1':
        print("PR with the title:", pr_data['title'], "and the id", pr_data['id'], "\n")
        created_at_time = datetime.fromisoformat(pr_data['created_at'].replace('Z', '+00:00'))
        current_time = datetime.now(timezone.utc)  # Convert current time to UTC
        difference = current_time - created_at_time
        if difference > timedelta(minutes=5):
            print(close_request(pr_data['number']))
        elif difference > timedelta(days=8) and difference < timedelta(days=10):
            print("For PR with title", pr_data['title'])
            email_func()