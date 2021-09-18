from jira_shortcut import get_jira_data
from tr_shortcut import *
import datetime


start_time = datetime.datetime.now()
jira_d = get_jira_data()
tr_cases = get_tr_cases()
tc_d = get_testrail_data(tr_cases)

temp = jira_d.keys()
good = 0
for key in temp:
    if key not in tc_d.keys():
        print(key + " " + jira_d[key])
    else:
        # die?
        good += 1


time = datetime.datetime.now() - start_time
with open('result2.txt', 'a') as r:
        r.write("\n" + str(time) + ", N/A")