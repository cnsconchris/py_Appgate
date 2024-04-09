# %%

import requests
import json
import warnings
import pandas as pd
import xlsxwriter
from datetime import datetime
import shutil

#Todos
#Create function from method classes instead of individual functions.
#Move url to input info file
#Document steps
#Logging
#Automation


warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made.*")

my_cred_info_file = '/Users/chris/code/PYTHON_TOOLS/Local/Appgate/alvaka_sdp_controller_info.json'
my_sdp_url = "https://alv-lassdpctl01.alvaka.net:8443/admin/"
#my_sdp_url = "https://ctlr1.lab.sdpdemo.com:8443/admin/"

my_output_dir = '/Users/chris/OneDriveAlvakaNetworks/ALV01/DataAnalysis/Appgate/'
my_output_file_prefix = 'alvaka_sdp_data'
my_output_file_extension = '.xlsx'

my_now = datetime.now()
my_timestamp = my_now.strftime('%Y%m%d_%H%M%S')
my_output_file_path = my_output_dir + my_output_file_prefix + '_' + my_timestamp + my_output_file_extension
my_output_file_path_no_timestamp = my_output_dir + my_output_file_prefix + my_output_file_extension


my_list_dfs = []


my_headers = {
    'Accept': 'application/vnd.appgate.peer-v19+json',
    'Content-Type': 'application/json'
}

def myf_save_json_file(my_file_desc,my_json_data):
    global my_timestamp
    global my_output_dir
    global my_output_file_prefix
    my_output_file_prefix_json = my_output_file_prefix + '_' + my_file_desc
    my_output_file_extension_json = '.json'
    my_output_file_path_json = my_output_dir + my_output_file_prefix_json + '_' + my_timestamp + my_output_file_extension_json
    
    with open(my_output_file_path_json, 'w') as my_json_file:
        json.dump(my_json_data, my_json_file, indent=4) 
    return
    


#URL Reqest function
def myf_url_request(my_method,my_url,my_headers,my_payload):
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

#Login Function
def myf_url_login():
    global my_sdp_url
    global my_cred_info_file
    global my_headers
    global my_headers_auth_data
    global my_token
    global my_token_expires
    global my_api_user_info
    global my_headers_auth_data
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
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    my_method = "POST"
    my_method_call = "authentication/logout"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)

    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)

    return my_response


#Get data functions

def myf_get_token_records():
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    my_method = "GET"
    my_method_call = "token-records"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
    my_response_json = my_response.json()
    # myf_save_json_file('token-records', my_response.json())
    return my_response


def myf_get_token_records_dn():
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    my_method = "GET"
    my_method_call = "token-records/dn"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
    my_response_json = my_response.json()
    # myf_save_json_file('token-records_dn', my_response.json())
    return my_response


def myf_get_admin_messages():
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    my_method = "GET"
    my_method_call = "admin-messages"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
    # myf_save_json_file('admin-messages', my_response.json())
    return my_response


def myf_get_admin_messages_summarize():
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    my_method = "GET"
    my_method_call = "admin-messages/summarize"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
    # myf_save_json_file('admin-messages_summarize', my_response.json())
    return my_response


def myf_get_entitlements():
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    global my_list_dfs
    global my_df_entitlements
    global my_df_entitlements_actions
    my_method = "GET"
    my_method_call = "entitlements"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
    # myf_save_json_file('entitlements', my_response.json())
    
    my_response_json = my_response.json()
    
    my_df_entitlements = pd.DataFrame.from_dict(my_response_json['data'])

    my_df_entitlements['actions'] = my_df_entitlements['actions']

    my_df_temp = None
    my_list_temp = None

    my_df_entitlements_actions = pd.DataFrame()
    for my_record_temp in my_response_json['data']:
        my_list_temp = my_record_temp['actions']   
        my_df_temp = pd.DataFrame(my_list_temp)
        my_df_temp.insert(0, 'ENTITLEMENT_id', my_record_temp['id'])
        my_df_temp.insert(1, 'ENTITLEMENT_name', my_record_temp['name'])
        my_df_entitlements_actions = pd.concat([my_df_entitlements_actions,my_df_temp ])
    my_list_dfs.append('my_df_entitlements')
    my_list_dfs.append('my_df_entitlements_actions')
    
    return my_response


def myf_get_policies():
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    global my_list_dfs
    global my_df_policies
    my_method = "GET"
    my_method_call = "policies"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
    # myf_save_json_file('policies', my_response.json())

    my_response_json = my_response.json()
    my_df_policies = pd.DataFrame.from_dict(my_response_json['data'])
    my_list_dfs.append('my_df_policies')
    
def myf_get_conditions():
    global my_sdp_urlb
    global my_headers
    global my_headers_auth_data
    global my_list_dfs
    global my_df_conditions
    my_method = "GET"
    my_method_call = "conditions"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
    # myf_save_json_file('conditions', my_response.json())

    my_response_json = my_response.json()
    my_df_conditions = pd.DataFrame.from_dict(my_response_json['data'])
    my_list_dfs.append('my_df_conditions')


#Future need to split
def myf_get_claims():
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    global my_list_dfs
    global my_df_claims
    my_method = "GET"
    my_method_call = "claims/names"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
    # myf_save_json_file('claims', my_response.json())

    my_response_json = my_response.json()
    
    #print(json.dumps(my_response_json, indent='\t'))
    my_df_claims = pd.DataFrame.from_dict(my_response_json['user'])
    #my_list_dfs.append('my_df_claims')


def myf_get_entitlement_scripts():
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    global my_list_dfs
    global my_df_entitlement_scripts
    my_method = "GET"
    my_method_call = "entitlement-scripts"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
    # myf_save_json_file('entitlement_scripts', my_response.json())

    my_response_json = my_response.json()
    my_df_entitlement_scripts = pd.DataFrame.from_dict(my_response_json['data'])
    my_list_dfs.append('my_df_entitlement_scripts')
    

def myf_get_criteria_scripts():
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    global my_list_dfs
    global my_df_criteria_scripts
    my_method = "GET"
    my_method_call = "criteria-scripts"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
    # myf_save_json_file('criteria_scripts', my_response.json())

    my_response_json = my_response.json()
    my_df_criteria_scripts = pd.DataFrame.from_dict(my_response_json['data'])
    my_list_dfs.append('my_df_criteria_scripts')

def myf_get_sites():
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    global my_list_dfs
    global my_df_sites
    my_method = "GET"
    my_method_call = "sites"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
    # myf_save_json_file('sites', my_response.json())

    my_response_json = my_response.json()
    my_df_sites = pd.DataFrame.from_dict(my_response_json['data'])
    my_list_dfs.append('my_df_sites')


def myf_get_entitlement_tags():
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    global my_list_dfs
    global my_df_entitlement_tags
    my_method = "GET"
    my_method_call = "entitlements/tags"
    my_url = my_sdp_url+my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_response = myf_url_request(my_method,my_url,my_headers,my_payload)
    # myf_save_json_file('entitlement_tags', my_response.json())

    my_response_json = my_response.json()
    print(json.dumps(my_response_json,indent='\t'))
    my_df_entitlement_tags = pd.DataFrame.from_dict(my_response_json)
    # my_list_dfs.append('my_df_entitlement_tags')


def myf_get_all_user_licenses():
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    global my_list_dfs
    global my_sdp_url
    global my_headers
    global my_headers_auth_data
    global my_list_dfs
    global my_df_all_user_licenses
    my_method = "GET"
    my_method_call = "license/users"
    my_url = my_sdp_url + my_method_call
    my_payload = None
    my_headers.update(my_headers_auth_data)
    my_params = my_xp
    my_response = myf_url_request(my_method, my_url, my_headers,  my_payload)
    # myf_save_json_file('all_user_licenses', my_response.json())

    my_response_json = my_response.json()
    print(json.dumps(my_response_json, indent='\t'))
    my_df_all_user_licenses = pd.DataFrame.from_dict(my_response_json['data'])
    #my_list_dfs.append('my_df_all_user_licenses')


my_response_login = myf_url_login()
# -----------------------------------------

# my_get_entitlements_response = myf_get_entitlements()
#
# my_get_policies_response = myf_get_policies()
#
# my_get_conditions_response = myf_get_conditions()
#
# my_get_entitlement_scripts = myf_get_entitlement_scripts()
#
# my_get_criteria_scripts = myf_get_criteria_scripts()
#
# my_get_sites = myf_get_sites()

my_get_all_user_licenses = myf_get_all_user_licenses()


# -----------------------------------------
my_response_logout = myf_url_logout()


# %%

with pd.ExcelWriter(my_output_file_path, engine='xlsxwriter') as my_xls_file:
    print('Exporting Data Frames to:', my_output_file_path)
    for my_item_df_name in my_list_dfs:
        print(my_item_df_name)
        my_df_item = globals()[my_item_df_name]
        my_sheet_name = my_item_df_name.replace('my_df_','')
        my_df_item.to_excel(my_xls_file, sheet_name=my_sheet_name, startrow=1, header=False, index=False)
        workbook = my_xls_file.book
        worksheet = my_xls_file.sheets[my_sheet_name]
        (max_row, max_col) = my_df_item.shape
        column_settings = [{'header': column} for column in my_df_item.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
        worksheet.set_column(0, max_col - 1, 12)
