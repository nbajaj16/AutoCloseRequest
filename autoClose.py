import inspect
import os
import requests
from datetime import datetime 
import pandas as pd
from datetime import timedelta

repo_owner, repo_name = "nbajaj16", "AutoCloseRequest"

api = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
api_for_email = f"https://api.github.com/users/{repo_owner}/events/public"
access_token = os.environ["access_token"]

def get_data(api):
    response = requests.get(api)
    return response.json()

api_call = get_data(api)

def email_func():
    return {}

def close_request(number):
    patch_api = f"{api}/{number}"
    data = {
        'state' : 'closed'
    } 
    headers = {
        "Authorization" : f"Bearer {access_token}"  # Replace with your GitHub access token
    }
    patch_request = requests.patch(patch_api, headers=headers, json=data)
    return patch_request.json()

# Check if the difference is more than 8 days for each open pull request
for data in api_call:
    if data['state'] == 'open':
        created_at_date = pd.to_datetime(data['created_at']).date()
        difference = datetime.now().date() - created_at_date
        if difference == timedelta(days=1):
            close_request(data['number'])
            print("Request Closed successfuly!")
        elif difference > timedelta(days=8) and difference < timedelta(days=10):
            email_func()
