from jira_shortcut import get_jira_data
from tr_shortcut import *
import datetime
import pandas as pd

# Objective of get_tc_coverage: go through data and figure out which tickets have test cases and which don't
# jira_d - dictionary of ticket:summary
# tr_d - dictionary of ticket:test case ID
# return - not_complete_df - a dataframe with data about tickets w/out test cases
# return - complete_df - a dataframe with data about ticket with test cases
def get_tc_coverage(jira_d, tr_d): 
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
# check Sportsbook project for linked cases
tc_d_SB = get_testrail_data(tr_client, 6) # a dictionary of jira tickets:linked test cases - sportsbook cross project

no_SB_tcs_df, SB_tcs_df = get_tc_coverage(jira_d, tc_d_SB)
# check Casino project for linked cases
if not no_SB_tcs_df.empty:
    tc_d_CAS = get_testrail_data(tr_client, 8) # a dictionary of jira tickets:linked test cases - casino cross project
    # convert dataframe columns into a dictionary so it can be passed into get_tc_coverage
    no_SB_tcs_dict = no_SB_tcs_df.set_index('Ticket').to_dict()['Summary']

    no_CAS_tcs_df, CAS_tcs_df = get_tc_coverage(no_SB_tcs_dict, tc_d_CAS)
    tcs_all = pd.concat([SB_tcs_df, CAS_tcs_df], ignore_index=True)

    # print to csv files - sportsbook & casino
    tcs_all.to_csv('./test_text_files/jazz_yes_cases.csv', sep='\t')
    no_CAS_tcs_df.to_csv('./test_text_files/jazz_no_cases.csv', sep='\t')

else:
    # print to csv files - sportsbook only
    no_SB_tcs_df.to_csv('./test_text_files/jazz_no_cases.csv', sep='\t')
    SB_tcs_df.to_csv('./test_text_files/jazz_yes_cases.csv', sep='\t')


time = datetime.datetime.now() - start_time
with open('./test_text_files/result2.txt', 'a') as r:
        r.write("\n" + str(time) + ", N/A")