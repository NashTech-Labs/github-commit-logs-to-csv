import requests
import json
import os
import csv
import pandas as pd
from dotenv import load_dotenv

# load environment variable from .env file
load_dotenv()

# define required variables
patToken = os.getenv("PAT_TOKEN")
branch = os.getenv("GITHUB_REF_NAME")
repositoryName = os.getenv("GITHUB_REPOSITORY")
header = {'Authorization': "Token "+patToken}
repo = repositoryName.split('/')[1]

# function to sort csv file by date
def sort_csv_by_date(file_path, sort_col):
    df = pd.read_csv(file_path)
    df.sort_values(by=[sort_col], inplace=True, ascending=False)
    df.to_csv(file_path, index=False, na_rep='None')

def get_commits(header, repositoryName, page=1, per_page=100):
    try:
        url = f"https://api.github.com/repos/{repositoryName}/commits?per_page={per_page}&page={page}"
        response = requests.get(url, headers=header).json()
    except:
        raise Exception(f"Failed to retrive commits: {response.text}")
    return response


page = 1
per_page = 100
commitList = []
while True:
    commits = get_commits(header, repositoryName, page, per_page)
    if not commits:
        break
    commitList.extend(commits)
    page += 1

# Write the commits to a csv file
csvFileName=f"{repo}_commits.csv"
with open(csvFileName, "w", newline='') as commitCSV:
    col_name = ["repository", "sha", "branch","author", "message", "html_url", "date"]
    writer = csv.DictWriter(commitCSV, fieldnames=col_name)
    writer.writeheader()

    # loop through commitList to get all commit data
    for commit in commitList:
        repository = repo
        sha = commit["sha"]
        branch = "main"
        author = commit["commit"]["author"]["name"]
        message = commit["commit"]["message"].replace("\n\n", "\n")
        html_url = commit["html_url"]
        date = commit["commit"]["author"]["date"]
        writer.writerow({"repository":repository, "sha":sha, "branch":branch, "author":author, "message":message, "html_url":html_url, "date":date})
    commitCSV.close()

sort_csv_by_date(csvFileName, "date")

print(f"Retrieved and wrote {len(commitList)} commits to the CSV file")