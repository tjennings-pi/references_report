from testrail import *
import os 
import json
import datetime

def setup_tr_client():
    # variables added to ~/.zshrc file
    email = os.getenv('PI_EMAIL')
    token = os.getenv('TESTRAIL_TOKEN')
    
    client = APIClient('http://hollywoodsports.testrail.io/')
    client.user = email
    client.password = token

    return client
"""
Objective of get_testrail_data: return tickets and their linked test cases
client - testrail client to make API calls
return - jira_tc - a dictionary of jira tickets:linked test cases
"""
def get_testrail_data(client, project):
    # get test cases from sportsbook project
    endpoint = f'get_cases/{project}'
    cases = client.send_get(endpoint)

    # this is just to help me see what the response from testrail looks like
    with open('./test_text_files/test1.txt', 'w') as f:
        for item in cases:
            f.write("%s\n" % item)

    jsonString = json.dumps(cases)
    #print(jsonString)
    case = json.dumps(json.loads(jsonString), sort_keys=True, indent=4, separators=(",", ": "))
    f = open("./test_text_files/test2.txt", "w")
    f.write(case)
    f.close()

    tc_jira = {}
    jira_tc = {}
    #cases_length = len(cases["cases"])
    iterations = 0

    while cases["_links"]["next"] != None or iterations == 0:
        cases_length = len(cases["cases"])
        # go through test case data
        for i in range(cases_length):
            # if test case contains references
            if cases["cases"][i]["refs"] != None:
                # split references string into a list
                split_cases = cases["cases"][i]["refs"].replace(" ","").split(",")
                # create a dictionary with key (test case id - string) value (test case references - list) pairs
                tc_jira[cases["cases"][i]["id"]] = split_cases
                # go through references
                for j in split_cases:
                    # if dictionary doesn't have an entry for the reference
                    if j not in jira_tc.keys():
                        # add reference to the dictionary with key (test case reference - string) value (list of test case ids (strings))
                        jira_tc[j] = [cases["cases"][i]["id"]]
                    # if dictionary does have an entry for the reference
                    else:
                        # append the test case id to the end of the list of test case ids (value of key-value pair)
                        jira_tc[j].append(cases["cases"][i]["id"])
        
        iterations +=1
        if cases["_links"]["next"] != None: 
            offset = cases["offset"] + 250
            req = f'get_cases/{project}&offset={offset}'
            cases = client.send_get(req)
            # check if next newly loaded cases are the last page
            if cases["_links"]["next"] == None:
                iterations = 0

    # print all test cases and their references to a text doc
    # prob wanna work on getting this into a dataframe or csv
    with open('./test_text_files/test3.txt', 'w') as g:
        g.write(json.dumps(json.loads(json.dumps(jira_tc)), sort_keys=True, indent=4, separators=(",", ": ")))

    return jira_tc

def timing_results():
    start_time = datetime.datetime.now()
    tr_client = setup_tr_client()
    # check Sportsbook project for linked cases
    tc_d_SB = get_testrail_data(tr_client, 6)
    time = datetime.datetime.now() - start_time

    with open('./test_text_files/result.txt', 'a') as r:
        r.write("\n" + str(datetime.date.today()) +" " + str(time) + ", run tr_shortcut.py")

if __name__ == "__main__":
    timing_results()