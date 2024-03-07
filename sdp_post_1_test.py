# %%
# Todos
# Etitlements todos
# riskSensitivity
# methods
# Tags not working

import requests
import json
import warnings
import pandas as pd
import xlsxwriter
from datetime import datetime
import shutil
import ast
import numpy as np

warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made.*")

my_cred_info_file = '/Users/chris/code/PYTHON_TOOLS/Local/Appgate/alvaka_sdp_controller_info.json'
my_sdp_url = "https://alv-lassdpctl01.alvaka.net:8443/admin/"

my_input_file_path = '/Users/chris/OneDriveAlvakaNetworks/ALV01/DataAnalysis/Appgate/sdp_data_input_2.xlsx'

my_headers = {
    'Accept': 'application/vnd.appgate.peer-v19+json',
    'Content-Type': 'application/json'
}


# URL Request function
def myf_url_request(my_method, my_url, my_headers, my_payload):
    print('----CALL START----')
    print('Method: ', my_method)
    print('URL:', my_url)
    print('Headers: ', my_headers)
    print('Payload:', my_payload)
    my_response = requests.request(my_method, my_url, headers=my_headers, data=my_payload, verify=False)
    print(my_response)
    print('----CALL END----')
    print('')
    return my_response


# Login Function
def myf_url_login():
    # global my_sdp_url
    # global my_cred_info_file
    # global my_headers
    # global my_headers_auth_data
    # global my_token
    # global my_token_expires
    # global my_api_user_info
    # global my_headers_auth_data
    my_method = "POST"
    my_method_call = "login"
    my_url = my_sdp_url+my_method_call
    
    with open(my_cred_info_file, 'r') as my_cred_json_file:
        my_cred_info_data = json.load(my_cred_json_file)

    my_payload = json.dumps(my_cred_info_data)

    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)

    my_response_login = my_response
    my_response_login_json = my_response_login.json()
    my_token = my_response_login_json['token']
    my_token_expires = my_response_login_json['expires']
    my_api_user_info = my_response_login_json['user']

    my_headers_auth_data = {
        "Authorization": "Bearer " + my_token
    }

    return my_response


# Logout Function
def myf_url_logout():
    # global my_sdp_url
    # global my_headers
    # global my_headers_auth_data
    my_method = "POST"
    my_method_call = "authentication/logout"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)

    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)

    return my_response


# Validate
def myf_get_entitlement_byid(my_ent_id):
    # global my_sdp_url
    # global my_headers
    # global my_headers_auth_data
    # global my_list_dfs
    # global my_df_entitlements_byid
    
    my_method = "GET"
    my_method_call = "entitlements"
    my_url = my_sdp_url+my_method_call + '/' + my_ent_id
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
   
    # my_response_json = my_response.json()
    # my_df_entitlement_byid = pd.DataFrame.from_dict(my_response_json['data'])
    return my_response


def myf_post(my_method_call,my_payload):
    # global my_sdp_url
    # global my_headers
    # global my_headers_auth_data
    my_method = "POST"
    my_url = my_sdp_url+my_method_call
        
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
   
    return my_response


def myf_put(my_method_call,my_payload,my_ent_id):
    # global my_sdp_url
    # global my_headers
    # global my_headers_auth_data
    my_method = "PUT"
    my_url = my_sdp_url+my_method_call + '/' + my_ent_id
        
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
   
    return my_response

# ---------- Login
my_response_login = myf_url_login()

# Load all sheets.   Get sheet names
my_dict_sheets  =  pd.read_excel(my_input_file_path, sheet_name=None).keys()
# my_df_sheets = pd.DataFrame(my_dict_sheets, columns=['SheetName'])
my_list_sheets = list(my_dict_sheets)

# Read entitlement actions
my_df_entitlement = pd.read_excel(my_input_file_path, sheet_name='entitlements')
my_df_entitlement_actions = pd.read_excel(my_input_file_path, sheet_name='entitlements_actions')

# my_df_distinct_input = my_df_entitlement_actions.drop_duplicates(subset=["ENTITLEMENT_id"])[["ENTITLEMENT_name"]]
# my_df_columns_input = my_df_entitlement_actions.columns


# Function to convert column values from strings to list for dictionary output
def myf_convert_to_list(my_string):
    if pd.isna(my_string):
        return np.nan
    else:
        return ast.literal_eval(my_string)


my_df_entitlement['tags'] = my_df_entitlement['tags'].apply(myf_convert_to_list)
my_df_entitlement['conditions'] = my_df_entitlement['conditions'].apply(myf_convert_to_list)
my_df_entitlement['conditionLinks'] = my_df_entitlement['conditionLinks'].apply(myf_convert_to_list)
my_df_entitlement['appShortcuts'] = my_df_entitlement['appShortcuts'].apply(myf_convert_to_list)
my_df_entitlement['appShortcutScripts'] = my_df_entitlement['appShortcutScripts'].apply(myf_convert_to_list)

my_df_entitlement_actions['hosts'] = my_df_entitlement_actions['hosts'].apply(myf_convert_to_list)
my_df_entitlement_actions['ports'] = my_df_entitlement_actions['ports'].apply(myf_convert_to_list)
my_df_entitlement_actions['monitor'] = my_df_entitlement_actions['monitor'].apply(myf_convert_to_list)
my_df_entitlement_actions['types'] = my_df_entitlement_actions['types'].apply(myf_convert_to_list)


my_df_entitlement = my_df_entitlement.fillna("")
my_df_entitlement_actions = my_df_entitlement_actions.fillna("")


# Used for testing of combining all dicts
# my_dict_main = []

for my_row in my_df_entitlement.itertuples():
    my_dict_entitlement = {}
   
    # print('MyEntID: ', my_row.id)
   
    my_df_matched = my_df_entitlement_actions[my_df_entitlement_actions['ENTITLEMENT_name'] == my_row.name]
    my_df_matched_stripped = my_df_matched.drop(columns=['ENTITLEMENT_id', 'ENTITLEMENT_name', 'monitor', 'id', 'type', 'ASSTRING_monitor'])
    my_dict_matched_stripped = my_df_matched_stripped.to_dict(orient='records')

    my_dict_entitlement['name'] = my_row.name
    my_dict_entitlement['notes'] = my_row.notes
    my_dict_entitlement['tags'] = my_row.tags
    my_dict_entitlement['disabled'] = my_row.disabled
    my_dict_entitlement['site'] = my_row.site
    # my_dict_entitlement['riskSensitivity'] = my_row.riskSensitivity
    my_dict_entitlement['conditionLogic'] = my_row.conditionLogic
    my_dict_entitlement['conditions'] = my_row.conditions
    my_dict_entitlement['conditionLinks'] = my_row.conditionLinks
    my_dict_entitlement['appShortcuts'] = my_row.appShortcuts
    my_dict_entitlement['appShortcutScripts'] = my_row.appShortcutScripts
    my_dict_entitlement['actions'] = my_dict_matched_stripped 

    # print(json.dumps(my_dict_entitlement,indent='\t'))
    
    my_payload = json.dumps(my_dict_entitlement)
    
    # print(my_payload)

    # Check to see if master list has Entity ID.
    if my_row.id != "":
        # check to see if Entity ID exists in SDP.
        myf_get_ent_byid_status_code = myf_get_entitlement_byid(my_row.id).status_code
        if myf_get_ent_byid_status_code == 200:
            my_response = myf_put('entitlements', my_payload, my_row.id)
        else:
            my_response = myf_post('entitlements', my_payload)    
    else:        
        my_response = myf_post('entitlements', my_payload)
    
    #print(my_response,'\n\n')
        
    # testing
    # my_dict_main.append(my_dict_entitlement)

# testing
# print(json.dumps(my_dict_main,indent='\t'))

# for my_pyload_dict in my_dict_main:
#     print('-----------Start Payload-------------')
#     print(json.dumps(my_pyload_dict,indent='\t'))
#     print('-----------End Payload-------------')






# ---------- Logout
my_response_login = myf_url_logout()
