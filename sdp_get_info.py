# %%
import sdp_login_and_logout
from sdp_login_and_logout import my_gvar_sdp_url

print(my_gvar_sdp_url)

# ------------- BEGIN LOG IN SCRIPT ---------------
my_login_response = sdp_login_and_out.myf_url_login()
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


# ------------- BEGIN LOG OUT SCRIPT ---------------
my_logout_response = sdp_login_and_out.myf_url_logout(my_login_headers_auth_data)
print('Logout Status Code: ', my_logout_response.status_code)
# ------------- BEGIN LOG OUT SCRIPT ---------------
