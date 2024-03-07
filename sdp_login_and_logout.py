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
global my_connect_info_file
global my_gvar_headers
global my_gvar_sdp_url


warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made.*")

my_connect_info_file = '/Users/chris/code/PYTHON_TOOLS/Local/Appgate/alvaka_sdp_connect_info.json'

# Testing of credential information and URL from file.
# NOTE: deviceID is the local device machine ID running a script.  Need to create SOP.

my_gvar_headers = {
    'Accept': 'application/vnd.appgate.peer-v19+json',
    'Content-Type': 'application/json'
}

with open(my_connect_info_file, 'r') as my_cred_json_file:
    my_connect_info_data = json.load(my_cred_json_file)

my_gvar_sdp_url = my_connect_info_data['sdp_url']['url']


def myf_url_login():
    with open(my_connect_info_file, 'r') as my_fvar_cred_json_file:
        my_fvar_connect_info_data = json.load(my_fvar_cred_json_file)

    my_fvar_sdp_cred_info = json.dumps(my_fvar_connect_info_data['sdp_cred_info'])
    my_fvar_sdp_url = my_gvar_sdp_url
    # print(my_fvar_sdp_cred_info)
    print('SDP URL: ', my_fvar_sdp_url)

    my_fvar_method = "POST"
    my_fvar_method_call = "login"
    my_fvar_url = my_fvar_sdp_url+my_fvar_method_call
    my_fvar_payload = my_fvar_sdp_cred_info
    my_fvar_headers = my_gvar_headers

    my_fvar_login_response = requests.request(my_fvar_method, my_fvar_url,
                                              headers=my_fvar_headers, data=my_fvar_payload, verify=False)

    return my_fvar_login_response


def myf_url_logout(my_fvar_headers_auth_data):
    my_fvar_sdp_url = my_gvar_sdp_url
    my_fvar_method = "POST"
    my_fvar_method_call = "authentication/logout"
    my_fvar_url = my_fvar_sdp_url + my_fvar_method_call
    my_fvar_payload = None
    my_fvar_headers = my_gvar_headers
    my_fvar_headers.update(my_fvar_headers_auth_data)

    my_fvar_logout_response = requests.request(my_fvar_method, my_fvar_url,
                                               headers=my_fvar_headers, data=my_fvar_payload, verify=False)

    return my_fvar_logout_response


# Main Function
def main():
    my_fvar_login_response = myf_url_login()
    return my_fvar_login_response


def main2(my_fvar_headers_auth_data):
    my_fvar_logout_response = myf_url_logout(my_fvar_headers_auth_data)
    return my_fvar_logout_response


# Check if the script is run directly
# Does a check to login, get token and log out.
if __name__ == "__main__":
    # Call the main function
    my_login_response = main()
    my_login_response_json = my_login_response.json()
    my_login_token = my_login_response_json['token']
    my_login_token_expires = my_login_response_json['expires']
    my_login_api_user_info = my_login_response_json['user']
    my_login_headers_auth_data = {
        "Authorization": "Bearer " + my_login_token
    }
    print('Login Status Code: ', my_login_response.status_code)
    print('Token Expires: ', my_login_token_expires, '\n\n\n')

    my_logout_response = main2(my_login_headers_auth_data)
    print('Logout Status Code: ', my_logout_response.status_code)





