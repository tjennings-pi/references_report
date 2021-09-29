from jira_shortcut import get_jira_data
from tr_shortcut import *
import datetime


start_time = datetime.datetime.now()
jira_d = get_jira_data()
if jira_d == 0:
    exit(0)
tr_client = setup_tr_client()
tc_d = get_testrail_data(tr_client)

temp = jira_d.keys()
good = 0
for key in temp:
    if key not in tc_d.keys():
        print(key + " " + jira_d[key])
    else:
        # die?
        good += 1


time = datetime.datetime.now() - start_time
with open('./test_text_files/result2.txt', 'a') as r:
        r.write("\n" + str(time) + ", N/A")