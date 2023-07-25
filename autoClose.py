import os
import requests
import yaml
import pandas as pd

from datetime import datetime 
from datetime import timedelta

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
access_token = "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"

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
    print(patch_api)
    patch_request = requests.patch(patch_api, headers=headers, json=data)
    return patch_request

for pr_data in pull_requests:
    if pr_data['state'] == 'open' and pr_data['base']['ref'] == 'b1':
        print("PR with the title :", pr_data['title'], "and the id", pr_data['id'])
        created_at_date = pd.to_datetime(pr_data['created_at']).date()
        difference = datetime.now().date() - created_at_date
        if difference > timedelta(days=10):
            close_request(pr_data['number'])
        elif difference > timedelta(minutes=8) and difference < timedelta(days=10):
            email_func()
