# This code sample uses the 'requests' library:
# http://docs.python-requests.org

# references
# 1. https://stackoverflow.com/questions/29996079/match-a-whole-word-in-a-string-using-dynamic-regex
# 2. https://stackoverflow.com/questions/63814822/check-if-input-consists-of-a-comma-separated-list-of-numbers

import os
import re
import requests
from requests.auth import HTTPBasicAuth
import json

# Objective of validate_input: make sure user input is in the  valid form
# What is the valid form? n or n,n,...,n; where n is a digit between 0 and upper_bounds minus 1
# input - user input (string), upper_bounds - number of entries in the selection list (int)
# return - True|False - boolean representing whether input matches valid form
def validate_input(input, upper_bounds):
   # reg expression base: ^[0-9](,[0-9]+)*$
   match_string = r'^[0-' + str(upper_bounds-1) + r'](,[0-' + str(upper_bounds-1) + r']+)*$' # reference 1
   pattern = re.compile(match_string) # reference 2
   match_result = re.search(pattern, input)
   if match_result:
      return True
   else:
      return False

# Objective of show_list_get_choice: display list and get user selection with validation
# Validation takes place in validate_input(input, upper_bounds)
# length - length of list (int), given_list - list to be displayed to user (array)
# return - query - a string with list items separated by a comma
def show_list_get_choice(length, given_list):
   # print list items
   for i in range(length):
      print("[", i, "] ", given_list[i])
   print("Selection: ")
   choice = input("> ")
   match = validate_input(choice, length)
   while match == False:
      print("Please make sure your selection contains only the given numbers in the following form: 0,1,2.\nSelection: ")
      choice = input("> ")
      match = validate_input(choice, length)
   split = choice.split(',')
   # changing value of split from number selection to corresponding list item
   for i in range(len(split)):
      split[i] = given_list[int(split[i])]
   query = ",".join(split)
   return query


# Objective of build_user_query: print user instructions & take in responses; use input to call validate_input & show_list_get_choice methods; build query
# return - user_query - a string of the query to be used in the jira request
def build_user_query():
   # projects
   projects = ["JAZZ", "STREET", "OP", "RAT"]
   p_length = len(projects)
   # types (New Feature has to be put in quotes bc JQL requires them when a name contains a space)
   types = ["Bug", "Epic", "Improvement", "Initiative", "\"New Feature\"", "Spike", "Story", "Task"]
   t_length = len(types)

   print("We will now build your filter. Please answer the following prompts.\n")
   
   # get project name(s)
   print("Below is a list of available projects to choose from. Please enter the number(s) corresponding to your choice of project. If more than one, please separate each number with a comma (ex: 1,3,4).")
   p_query = show_list_get_choice(p_length, projects)

   # get issue type(s)
   print("Enter the number that corresponds to the issue types on which you would like to filter")
   print("[ 0 ]: All Standard Issue Types\n[ 1 ]: Specific Issue Types\nSelection: ")
   type = input("> ")
   while type not in ("0", "1"): 
      print("Please enter either 0 or 1 to make your selection.\nSelection: ")
      type = input("> ")
   # jira has a funtion for all standard issue types
   if type == "0":
      t_choice = "standardIssueTypes()"
      t_query = t_choice
   # figure out which issue types the user wnats
   else:
      print("Below is a list of the issue types you may select. Please enter the number(s) corresponding to your choice of issue type. If more than one, please separate each number with a comma (ex: 1,3,4).")
      t_query = show_list_get_choice(t_length, types)

   # get version(s)
   print("Please enter the fix version you would like to filter by. If more than one, please separate each fix version with a comma (ex: Magic,Nuggets).")
   v_query = input("> ")

   # get component(s)
   c_query = "iOS,\"AND\",WWW,QA"
   
   # building query
   user_query = f"project in ({p_query}) AND issuetype in ({t_query}) AND fixVersion in ({v_query}) AND component in ({c_query})"
   
   return user_query

# Objective of send_jira_search_request: set up & send jira search request
# jql_ query - string of the query to be used in the jira request
# return - response - requests.models.Response aka response from Jira
def send_jira_search_request(jql_query):
   # variables added to ~/.zshrc file
   email = os.getenv('PI_EMAIL')
   token = os.getenv('JIRA_TOKEN')
   endpoint = "/rest/api/3/search"
   url = f"https://penngineering.atlassian.net{endpoint}"

   auth = HTTPBasicAuth(email, token)

   headers = {
      "Accept": "application/json",
      "Content-Type": "application/json"
   }
   query = {
      'jql': jql_query,
      'fields': "summary",
      'maxResults': 100
   }
   response = requests.request(
      "GET",
      url,
      #data=payload,
      headers=headers,
      params=query,
      auth=auth
   )

   print(type(response))

   return response
     
# Objective of get_jira_data: return tickets and summaries (titles)
# return value - d - a dictionary of jira tickets:summaries
def get_jira_data():
   all_results = False # if response contains end of results or if it's paginated
   pointer = 0 # keeps track of page number
   key_list = []
   summary_list = []
   d = {} # dictionary of ticket numbers (keys) and titles/summaries (values)
   jql_query = build_user_query()

   while all_results == False:
      response = send_jira_search_request(jql_query)

      # holder is <class 'dict'>
      holder = json.loads(response.text)
      # this is just to help me see what the response looks like
      result = json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
      f = open("./test_text_files/test.txt", "w")
      f.write(result)
      f.close()

      # check if errors from jira
      if response.status_code != 200:
         print("-----ERROR-----")
         print("There was an issue with the Jira API request.")
         print("Response Status: " + str(response.status_code))
         print(holder)
         return 0
      
      # check if any results from jira
      if len(holder['issues']) == 0:
         print("Exiting program...\nNo issues found in this filter.")
         return 0

      # check if results are paginated
      pointer = pointer + holder['maxResults']
      if pointer < holder['total']:
         all_results = False
         # append page results to lists
         for i in range(len(holder["issues"])):
            key_list.append(holder["issues"][i].get('key'))
            summary_list.append(holder["issues"][i].get('fields').get('summary'))
            d[holder["issues"][i].get('key')] = holder["issues"][i].get('fields').get('summary')
         # update query to start at 'next page'
         query = {
            'jql': jql_query,
            'fields': "summary",
            'maxResults': 500,
            'startAt': pointer
         }

      else:
         all_results = True
         # append page results to lists
         for i in range(len(holder["issues"])):
            key_list.append(holder["issues"][i].get('key'))
            summary_list.append(holder["issues"][i].get('fields').get('summary'))
            d[holder["issues"][i].get('key')] = holder["issues"][i].get('fields').get('summary')

   with open('./test_text_files/test1_1.txt', 'w') as g:
      g.write(json.dumps(json.loads(json.dumps(d)), sort_keys=True, indent=4, separators=(",", ": ")))
   
   return d