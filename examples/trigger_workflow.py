# Based off https://stackoverflow.com/questions/69479400/get-run-id-after-triggering-a-github-workflow-dispatch-event

import random
import string
import datetime
import requests
from time import sleep
import json
import sys

# The following variables are required
owner = "NCIOCPL"
repo = "teams-notifications"
workflow = "digital_platform_dev.yml"
github_pat = sys.argv[1]  # Don't commit your secrets

# Using basic GitHub API authentication
authHeader = {"Authorization": f"Token {github_pat}"}

# Generate a random ID
run_identifier = "".join(random.choices(string.ascii_uppercase + string.digits, k=15))
# Only look at runs in the last 5 minutes
delta_time = datetime.timedelta(minutes=5)
run_date_filter = (datetime.datetime.now(datetime.timezone.utc) - delta_time).strftime(
    "%Y-%m-%dT%H:%M"
)

# Fire off our workflow with the run identifier
r = requests.post(
    f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow}/dispatches",
    headers=authHeader,
    json={
        "ref": "main",
        "inputs": {"subject": "Workflow triggered by python", "body": "Additional details to post to the workflow summary", "id": run_identifier},
    },
)
print(
    f"Dispatch workflow status: {r.status_code} | Workflow identifier: {run_identifier}"
)

# Looping code to check for our workflow ID
run_id = ""
checked_jobs = []
while run_id == "":

    # Get a list of all workflow runs currently showing up and extract their jobs lists
    r = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/actions/runs?created=%3E{run_date_filter}",
        headers=authHeader,
    )
    runs = r.json()["workflow_runs"]
    jobs_urls = [run["jobs_url"] for run in runs if run["jobs_url"] not in checked_jobs]
    print(f"Found {len(jobs_urls)} workflow run to check")

    # For each jobs list, check it to see if it has our workflow ID in it
    for url in jobs_urls:
        run_complete = False
        while not run_complete:

            # Get the jobs list for this particular workflow run
            r = requests.get(url, headers=authHeader)
            response = r.json()["jobs"]
            run = response[0]
            print(f"Checking workflow run with ID {run['id']} for our run identifier")

            # Check for completion and our workflow ID
            if run["status"] == "completed":
                run_complete = True
                if run["steps"][1]["name"] == run_identifier:
                    # We found our workflow ID
                    run_id = run["run_id"]
                else:
                    # If this workflow run's jobs were complete and did not have our ID then don't check again in the future
                    print(f'Workflow run has run identifier {run["steps"][1]["name"]} != {run_identifier}')
                    checked_jobs.append(url)

            # If the run isn't complete, briefly wait before we try again
            print(f"Run {run['id']} isn't complete yet")
            sleep(3)

    # If it doesn't, briefly wait before we try again
    sleep(3)

print(f"Run identifier found in run_id: {run_id}")

# Re-run our workflow as a demonstration
r = requests.post(
    f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
    headers=authHeader
)
print(
    f"Re-run request status: {r.status_code} | Run ID: {run_id}"
)