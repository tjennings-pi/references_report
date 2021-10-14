from jira_shortcut import get_jira_data
from tr_shortcut import *
import datetime
import pandas as pd

def dictionary_way(jira_d, tr_d): 
    temp = jira_d.keys()
    not_compete_df = pd.DataFrame(columns=['Ticket', 'Link', 'Summary'])
    compete_df = pd.DataFrame(columns=['Ticket', 'Link', 'Summary', 'Cases'])
    for key in temp:
        link = f'https://penngineering.atlassian.net/browse/{key}'
        if key not in tr_d.keys():
            not_compete_df = not_compete_df.append({'Ticket' : key, 'Summary' : jira_d[key], 'Link' : link}, ignore_index=True)
        else:
            # die?
            case_list = ', '.join(map(str, tr_d[key]))
            compete_df = compete_df.append({'Ticket': key, 'Link': link, 'Summary': jira_d[key], 'Cases': case_list}, ignore_index=True)
    return not_compete_df, compete_df

start_time = datetime.datetime.now()

# get jira tickets & testrail cases
jira_d = get_jira_data() # a dictionary of jira tickets:summaries
if jira_d == 0:
    exit(0)
tr_client = setup_tr_client()
tc_d_SB = get_testrail_data(tr_client, 6) # a dictionary of jira tickets:linked test cases - sportsbook cross project

no_SB_tcs_df, SB_tcs_df = dictionary_way(jira_d, tc_d_SB)
if not no_SB_tcs_df.empty:
    tc_d_CAS = get_testrail_data(tr_client, 8) # a dictionary of jira tickets:linked test cases - casino cross project
    # print(tc_d_CAS)
    no_SB_tcs_dict = no_SB_tcs_df.set_index('Ticket').to_dict()['Summary']
    no_CAS_tcs_df, CAS_tcs_df = dictionary_way(no_SB_tcs_dict, tc_d_CAS)
    tcs_all = pd.concat([SB_tcs_df, CAS_tcs_df], ignore_index=True)
    tcs_all.to_csv('./test_text_files/jazz_yes_cases.csv', sep='\t')
    no_CAS_tcs_df.to_csv('./test_text_files/jazz_no_cases.csv', sep='\t')

else:
    no_SB_tcs_df.to_csv('./test_text_files/jazz_no_cases.csv', sep='\t')
    SB_tcs_df.to_csv('./test_text_files/jazz_yes_cases.csv', sep='\t')
time = datetime.datetime.now() - start_time
with open('./test_text_files/result2.txt', 'a') as r:
        r.write("\n" + str(time) + ", N/A")