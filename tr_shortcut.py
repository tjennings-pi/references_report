from testrail import *
import os 
import json
import datetime

def get_tr_cases():
    # variables added to ~/.zshrc file
    email = os.getenv('PI_EMAIL')
    token = os.getenv('TESTRAIL_TOKEN')
    
    client = APIClient('http://hollywoodsports.testrail.io/')
    client.user = email
    client.password = token

    cases = client.send_get('get_cases/6')
    return cases

def get_testrail_data(cases):
    #cases = get_tr_cases()
    tc_jira = {}
    jira_tc = {}
    cases_length = len(cases)

    # go through test case data
    for i in range(cases_length):
        # if test case contains references
        if cases[i]["refs"] != None:
            # split references string into a list
            split_cases = cases[i]["refs"].replace(" ","").split(",")
            # create a dictionary with key (test case id - string) value (test case references - list) pairs
            tc_jira[cases[i]["id"]] = split_cases
            # go through references
            for j in split_cases:
                # if dictionary doesn't have an entry for the reference
                if j not in jira_tc.keys():
                    # add reference to the dictionary with key (test case reference - string) value (list of test case ids (strings))
                    jira_tc[j] = [cases[i]["id"]]
                # if dictionary does have an entry for the reference
                else:
                    # append the test case id to the end of the list of test case ids (value of key-value pair)
                    jira_tc[j].append(cases[i]["id"])

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

    # print all test cases and their references to a text doc
    # prob wanna work on getting this into a dataframe or csv
    with open('./test_text_files/test3.txt', 'w') as g:
        g.write(json.dumps(json.loads(json.dumps(jira_tc)), sort_keys=True, indent=4, separators=(",", ": ")))

    return jira_tc

def timing_results():
    start_time = datetime.datetime.now()
    tr_cases = get_tr_cases()
    tc_data = get_testrail_data(tr_cases)
    time = datetime.datetime.now() - start_time

    with open('./test_text_files/result.txt', 'a') as r:
        r.write("\n" + str(time) + ", return jira_tc instead of tc_jira")