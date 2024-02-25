# %%

import requests
import json
import warnings
import pandas as pd


url = "https://alv-lassdpctl01.alvaka.net:8443/admin/login"

warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made.*")

payload = json.dumps({
  "providerName": "local",
  "username": "api_chris",
  "password": "nopass$123",
  "deviceId": "FACCE489-6E97-4119-AB5A-A6336F7730FC"
})

headers = {
  'Accept': 'application/vnd.appgate.peer-v19+json',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload, verify=False)


my_response = response.json()
my_token = my_response['token']
my_token_expires = my_response['expires']
my_api_user_info = my_response['user']

my_df = pd.DataFrame(response)


my_url = "https://alv-lassdpctl01.alvaka.net:8443/admin/"
my_method = "GET"
my_method_call = "admin-messages"

my_auth_headers = {
    "Authorization": "Bearer " + my_token,
    'Accept': 'application/vnd.appgate.peer-v19+json',
    'Content-Type': 'application/json'
}

my_response = requests.request(my_method, my_url+my_method_call, headers=my_auth_headers, verify=False)
my_response_json = my_response.json()
my_response_data = my_response_json['data']
my_df_admin_messages = pd.DataFrame(my_response_data)


my_url = "https://alv-lassdpctl01.alvaka.net:8443/admin/"
my_method = "GET"
my_method_call = "admin-messages/summarize"

my_auth_headers = {
    "Authorization": "Bearer " + my_token,
    'Accept': 'application/vnd.appgate.peer-v19+json',
    'Content-Type': 'application/json'
}


my_response = requests.request(my_method, my_url+my_method_call, headers=my_auth_headers, verify=False)
my_response_json = my_response.json()
my_response_data = my_response_json['data']
my_df_admin_messages_summary = pd.DataFrame(my_response_data)


#print(json.dumps(my_admin_messages['data'], indent=4))





#Tokens

my_url = "https://alv-lassdpctl01.alvaka.net:8443/admin/"
my_method = "GET"
my_method_call = "token-records"

#token-records/dn
my_params = {
    #
    #'tokenId': '649e630a-2e7c-4edd-bd5f-864a165e0333'
    'revoked' : 'false'
    # 'query' :  [{'revoked=False'}],
    # 'filterBy' : [{'revoked=False'}]
}


my_xp = json.dumps(my_params)


my_auth_headers = {
    "Authorization": "Bearer " + my_token,
    'Accept': 'application/vnd.appgate.peer-v19+json',
    'Content-Type': 'application/json'
}

my_responsex = requests.request(my_method, my_url+my_method_call, headers=my_auth_headers, params=my_xp ,verify=False)
my_response_jsonx = my_responsex.json()
#my_response_json
my_response_data_x = my_response_jsonx['data']
my_df_active_devices = pd.DataFrame(my_response_data_x)
print(my_response_jsonx)

#List all entitlements

my_url = "https://alv-lassdpctl01.alvaka.net:8443/admin/"
my_method = "GET"
my_method_call = "entitlements"


my_auth_headers = {
    "Authorization": "Bearer " + my_token,
    'Accept': 'application/vnd.appgate.peer-v19+json',
    'Content-Type': 'application/json'
}

my_response = requests.request(my_method, my_url+my_method_call, headers=my_auth_headers ,verify=False)
my_response_json = my_response.json()
#my_response_json
my_response_data = my_response_json['data']
my_df_entitlements = pd.DataFrame(my_response_data)

#print(my_df_entitlements)




# Logout


url2 = "https://alv-lassdpctl01.alvaka.net:8443/admin/authentication/logout"
headers2 = {
    "Authorization": "Bearer " + my_token,
    'Accept': 'application/vnd.appgate.peer-v19+json',
    'Content-Type': 'application/json'
}
response2 = requests.request("POST", url2, headers=headers2,  verify=False)

#print(json.dumps(my_api_user_info, indent=2))