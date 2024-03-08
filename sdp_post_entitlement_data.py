# %%
import requests
import json
import warnings
import pandas as pd
import xlsxwriter
from datetime import datetime
import shutil
import ast
import numpy as np
import sdp_login_and_logout
from sdp_login_and_logout import my_gvar_sdp_url
from sdp_login_and_logout import my_gvar_headers

my_input_file_path = ('/Users/chris/OneDriveAlvakaNetworks/ALV01/'
                      'DataAnalysis/Appgate/alvaka_sdp_data_build_output.xlsx')


# Validate
def myf_get_entitlement_byid(my_fvar_login_headers_auth_data, my_fvar_ent_id):
    my_fvar_method = "GET"
    my_fvar_method_call = "entitlements"
    my_fvar_sdp_url = my_gvar_sdp_url
    my_fvar_url = my_fvar_sdp_url + my_fvar_method_call + '/' + my_fvar_ent_id
    my_fvar_payload = None
    my_fvar_headers = my_gvar_headers
    my_fvar_headers.update(my_fvar_login_headers_auth_data)
    my_fvar_response = requests.request(my_fvar_method, my_fvar_url,
                                        headers=my_fvar_headers, data=my_fvar_payload, verify=False)
    return my_fvar_response


def myf_post(my_fvar_login_headers_auth_data, my_fvar_method_call, my_fvar_payload):
    my_fvar_method = "POST"
    my_fvar_sdp_url = my_gvar_sdp_url
    my_fvar_url = my_fvar_sdp_url + my_fvar_method_call
    my_fvar_headers = my_gvar_headers
    my_fvar_headers.update(my_fvar_login_headers_auth_data)
    my_fvar_response = requests.request(my_fvar_method, my_fvar_url,
                                        headers=my_fvar_headers, data=my_fvar_payload, verify=False)
    return my_fvar_response


def myf_put(my_fvar_login_headers_auth_data, my_fvar_method_call, my_fvar_payload, my_fvar_ent_id):
    my_fvar_method = "PUT"
    my_fvar_sdp_url = my_gvar_sdp_url
    my_fvar_url = my_fvar_sdp_url + my_fvar_method_call + '/' + my_fvar_ent_id
    my_fvar_headers = my_gvar_headers
    my_fvar_headers.update(my_fvar_login_headers_auth_data)
    my_fvar_response = requests.request(my_fvar_method, my_fvar_url,
                                        headers=my_fvar_headers, data=my_fvar_payload, verify=False)
    return my_fvar_response


# ------------- BEGIN LOG IN SCRIPT ---------------
my_login_response = sdp_login_and_logout.myf_url_login()
my_login_response_json = my_login_response.json()
my_login_token = my_login_response_json['token']
my_login_token_expires = my_login_response_json['expires']
my_login_api_user_info = my_login_response_json['user']
my_login_headers_auth_data = {
    "Authorization": "Bearer " + my_login_token
}
print('Login Status Code: ', my_login_response.status_code)
print('Token Expires: ', my_login_token_expires, '\n\n\n')
# ------------- END LOG IN SCRIPT ---------------

# Test get ent by id
# my_ent_id = '52fe3d69-21f3-48ff-96d8-0c2c0ee308e4'
# my_get_ent_byid_status_code = myf_get_entitlement_byid(my_login_headers_auth_data, my_ent_id).status_code
# print(my_get_ent_byid_status_code)

# Load all sheets.   Get sheet names
my_dict_sheets = pd.read_excel(my_input_file_path, sheet_name=None).keys()
# my_df_sheets = pd.DataFrame(my_dict_sheets, columns=['SheetName'])
my_list_sheets = list(my_dict_sheets)

# Read entitlement actions
my_df_entitlement = pd.read_excel(my_input_file_path, sheet_name='entitlements')
my_df_entitlement_actions = pd.read_excel(my_input_file_path, sheet_name='entitlements_actions')


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

    print('MyEntID: ', my_row.id, my_row.name)

    my_df_matched = my_df_entitlement_actions[my_df_entitlement_actions['ENTITLEMENT_name'] == my_row.name]
    my_df_matched_stripped = my_df_matched.drop(
        columns=['ENTITLEMENT_id', 'ENTITLEMENT_name', 'monitor', 'id', 'type'])
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
        my_get_ent_byid_status_code = myf_get_entitlement_byid(my_login_headers_auth_data, my_row.id).status_code
        if my_get_ent_byid_status_code == 200:
            # my_fvar_login_headers_auth_data, my_fvar_method_call, my_fvar_payload)
            my_response = myf_put(my_login_headers_auth_data, 'entitlements', my_payload, my_row.id)

        else:
            my_response = myf_post(my_login_headers_auth_data, 'entitlements', my_payload)
    else:
        my_response = myf_post(my_login_headers_auth_data, 'entitlements', my_payload)

    print(my_response.status_code)
    if my_response.status_code == 409:
        print('Name exists with different ID!')
    print('')

    #print(my_response.json())
# ------------- BEGIN LOG OUT SCRIPT ---------------
my_logout_response = sdp_login_and_logout.myf_url_logout(my_login_headers_auth_data)
print('Logout Status Code: ', my_logout_response.status_code)
# ------------- BEGIN LOG OUT SCRIPT ---------------
