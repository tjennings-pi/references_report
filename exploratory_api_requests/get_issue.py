# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import os
import requests
from requests.auth import HTTPBasicAuth
import json

# variables added to ~/.zshrc file
email = os.getenv('PI_EMAIL')
token = os.getenv('JIRA_TOKEN')

issueID = "jazz-1140"
endpoint = f"/rest/api/3/issue/{issueID}"
url = f"https://penngineering.atlassian.net{endpoint}"

# ideally would not have email & token hard coded.
auth = HTTPBasicAuth(email, token)

headers = {
   "Accept": "application/json"
}

response = requests.request(
   "GET",
   url,
   headers=headers,
   auth=auth
)

# prints json nicely
print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
