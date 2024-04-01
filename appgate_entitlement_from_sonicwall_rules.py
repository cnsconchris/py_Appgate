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
import ipaddress
import sys

my_input_file_dir = '/Users/chris/OneDriveAlvakaNetworks/ALV01/DataAnalysis/Appgate/'
my_input_file = 'alv-las-ct-fw-1_20240319a_rules_20240319_174823_130423_more_20240319_181026.xlsx'
my_input_file_path = my_input_file_dir + my_input_file

# my_output_dir = '/Users/chris/OneDriveAlvakaNetworks/ALV01/DataAnalysis/Appgate/'
# my_output_file_prefix = 'alv-las-ct-f-w-1_for_appgate_build'
# my_output_file_extension = '.xlsx'

# my_now = datetime.now()
# my_timestamp = my_now.strftime('%Y%m%d_%H%M%S')
# # my_output_file_path = my_output_dir + my_output_file_prefix + '_' + my_output_file_extension
# my_output_file_path = my_output_dir + my_output_file_prefix + '_' + my_timestamp + my_output_file_extension
# my_output_file_path_no_timestamp = my_output_dir + my_output_file_prefix + my_output_file_extension

# Load all sheets
# Get sheet names
# Convert dict to list
# my_list_sheets = list(pd.read_excel(my_input_file_path, sheet_name=None).keys())
# print(my_list_sheets)
my_list_sheets = ['proc_fw_pol_vpn']

# Loop through sheet names and create global dataframe for each sheet
for my_sheet_item in my_list_sheets:
    globals()['my_df_' + my_sheet_item] = pd.read_excel(
        my_input_file_path, sheet_name=my_sheet_item
    )

# The dataframe to process to get entitlement output.
my_df_fw_pol_vpn = globals()['my_df_proc_fw_pol_vpn']

# Appgate entitlement dataframe temp.
my_list_entitlements_actions_cols = ['PolicyName', 'name', 'tags', 'type', 'action', 'hosts', 'subtype',
                                     'ports', 'types']
my_df_entitlements_actions = pd.DataFrame(columns=my_list_entitlements_actions_cols)

# Loop through sheet to create entitlements and entitlement actions tables.
for my_row_rule in my_df_fw_pol_vpn.itertuples():
    # Only process policyAction ALLOW rules and non VPN-SUBNETS sources.
    if (my_row_rule.policyAction == 'ALLOW' and my_row_rule.policySrcNet.find('VPN-SUBNETS') == -1
           ):
        # Create source tag

        if 'ALV-LAS-CT-SMAV-1' in my_row_rule.policyName:
            my_row_entitlement_tag = 'ALV01_ROLE-' + \
                                     my_row_rule.policyName.replace('ALV-LAS-CT-SMAV-1_', '').split('>')[0]
        elif 'ALV-LAS-CT-SSLVPN-1_' in my_row_rule.policyName:
            my_row_entitlement_tag = 'ALV01_ROLE-' + \
                                     my_row_rule.policyName.replace('ALV-LAS-CT-SSLVPN-1_', '').split('>')[0]
        else:
            my_row_entitlement_tag = ''

        my_row_entitlement_name = 'ALV01_' + my_row_rule.policyName.split('>')[-1]
        my_row_entitlement_type = 'IpAccess'
        my_row_entitlement_action = 'allow'

        if my_row_rule.DstProcessedAddress == 'ANY':
            my_row_entitlement_hosts = ['0.0.0.0/0']
        else:
            my_row_entitlement_hosts = my_row_rule.DstProcessedAddress

        if my_row_rule.DstGroupedDictService != 'ANY':
            my_row_services = my_row_rule.DstGroupedDictService
            my_row_services = ast.literal_eval(my_row_services)
            my_df_row_actions = pd.DataFrame.from_dict(my_row_services)
            # print(my_row_entitlement_name)

            # Get unique protocol types as action type and loop through actions to create separate rules per type
            my_list_actions_types = my_df_row_actions['type'].unique()
            for my_row_actions_type in my_list_actions_types:
                my_df_row_action = my_df_row_actions[my_df_row_actions['type'] == my_row_actions_type]
                my_row_entitlement_subtype = my_row_actions_type + '_up'
                if my_row_actions_type == 'icmp':
                    my_row_entitlement_types = ['0-255']
                    my_row_entitlement_ports = np.nan
                else:
                    my_row_entitlement_types = np.nan
                    my_row_entitlement_ports = my_df_row_action['ports'].iloc[0]

                my_row_entitlements_actions_rule = [{'PolicyName': my_row_rule.policyName,
                                                    'name': my_row_entitlement_name,
                                                    'tags':  my_row_entitlement_tag,
                                                    'type': my_row_entitlement_type,
                                                    'action': my_row_entitlement_action,
                                                    'hosts': my_row_entitlement_hosts,
                                                    'subtype': my_row_entitlement_subtype,
                                                    'ports': my_row_entitlement_ports,
                                                    'types': my_row_entitlement_types}]
                my_df_row_entitlements_actions_rule = pd.DataFrame(my_row_entitlements_actions_rule)
                my_df_entitlements_actions = pd.concat([my_df_entitlements_actions,
                                                        my_df_row_entitlements_actions_rule], ignore_index=True)

        elif my_row_rule.DstGroupedDictService == 'ANY':
            my_list_protocols_any = ['tcp', 'udp', 'icmp']
            for my_row_protocol in my_list_protocols_any:
                if my_row_protocol == 'tcp' or my_row_protocol == 'udp':
                    my_row_entitlement_ports = ['1-65535']
                    my_row_entitlement_types = np.nan
                elif my_row_protocol == 'icmp':
                    my_row_entitlement_ports = np.nan
                    my_row_entitlement_types = ['0-255']
                else:
                    print("For each protocol non ICMP TCP or UDP FOUND")
                    sys.exit()

                my_row_entitlement_subtype = my_row_protocol + '_up'

                my_row_entitlements_actions_rule = [{'PolicyName': my_row_rule.policyName,
                                                     'name': my_row_entitlement_name,
                                                     'tags': my_row_entitlement_tag,
                                                     'type': my_row_entitlement_type,
                                                     'action': my_row_entitlement_action,
                                                     'hosts': my_row_entitlement_hosts,
                                                     'subtype': my_row_entitlement_subtype,
                                                     'ports': my_row_entitlement_ports,
                                                     'types': my_row_entitlement_types}]
                my_df_row_entitlements_actions_rule = pd.DataFrame(my_row_entitlements_actions_rule)
                my_df_entitlements_actions = pd.concat([my_df_entitlements_actions,
                                                        my_df_row_entitlements_actions_rule], ignore_index=True)

        else:
            print('BREAK: dstGroupedDictService bypassed ANY or NOT ANY in IF ELSE')
            sys.exit()

    else:
        pass

# Make then convert list in my_df_entitlements_actions['ports'] to string
my_df_entitlements_actions['hosts'] = my_df_entitlements_actions[
    'hosts'].astype(str)

my_df_entitlements_actions['ports'] = my_df_entitlements_actions[
    'ports'].astype(str)

my_df_entitlements_actions['types'] = my_df_entitlements_actions[
    'types'].astype(str)

# Create entitlement actions dataframe.  This dataframe is a sublilst of entitlements used for API processing.
my_df_proc_entitlements_actions = my_df_entitlements_actions.drop(columns=['PolicyName', 'tags'])
my_df_proc_entitlements_actions_unique = my_df_proc_entitlements_actions.drop_duplicates().reset_index(drop=True)

my_df_proc_entitlements = pd.DataFrame()
my_df_proc_entitlements['name'] = my_df_entitlements_actions['name'].unique()


# Function to loop through entitlements to match tags to entitlement names and combine tags into a list for each
# entitlement name.
def myf_entitlement_tags(my_ent_name):
    my_df_temp = my_df_entitlements_actions[ my_df_entitlements_actions['name'] == my_ent_name]
    my_list = []
    for my_row in my_df_temp.itertuples():
        my_list.append(my_row.tags)

    # Remove Duplicates
    my_list = list(set(my_list))
    # Remove bland values
    my_list = [item for item in my_list if item != '']
    return my_list


my_df_proc_entitlements['tags'] = my_df_proc_entitlements.apply(
    lambda row: myf_entitlement_tags(row['name']), axis=1)

# Make then convert list in my_df_proc_entitlements['tags'] to string
my_df_proc_entitlements['tags'] = my_df_proc_entitlements['tags'].astype(str)

# Open up sdp data build for update
my_input_file_path_sdp_build = ('/Users/chris/OneDriveAlvakaNetworks/ALV01/'
                                'DataAnalysis/Appgate/alvaka_sdp_data_build_input.xlsx')
my_output_file_path_sdp_build = ('/Users/chris/OneDriveAlvakaNetworks/ALV01/'
                                 'DataAnalysis/Appgate/alvaka_sdp_data_build_output2.xlsx')

# Load all sheets.   Get sheet names
my_dict_sheets_sdp_build = pd.read_excel(my_input_file_path_sdp_build, sheet_name=None).keys()
my_list_sheets_sdp_build = list(my_dict_sheets_sdp_build)

# Read entitlement actions
my_df_sdp_ents_wfw_updates = pd.read_excel(my_input_file_path_sdp_build, sheet_name='entitlements')
my_df_sdp_ents_actions_wfw_updates = pd.read_excel(my_input_file_path_sdp_build, sheet_name='entitlements_actions')


# Prep and add defaults for update.
my_df_sdp_entitlements_fw_update = my_df_proc_entitlements
# Replace unsupported characters on SDP
my_df_sdp_entitlements_fw_update['name'] = my_df_sdp_entitlements_fw_update['name'].str.replace('/', '_', regex=False)
my_df_sdp_entitlements_fw_update['name'] = my_df_sdp_entitlements_fw_update['name'].str.replace('(', '', regex=False)
my_df_sdp_entitlements_fw_update['name'] = my_df_sdp_entitlements_fw_update['name'].str.replace(')', '', regex=False)
my_df_sdp_entitlements_fw_update['site'] = '8a4add9e-0e99-4bb1-949c-c9faf9a49ad4'
my_df_sdp_entitlements_fw_update['siteName'] = 'ALV-LAS-CT'
my_df_sdp_entitlements_fw_update['actions'] = 'READ_FROM_ENTITLEMENT_ACTIONS'
my_df_sdp_entitlements_fw_update['conditionLogic'] = 'and'
my_df_sdp_entitlements_fw_update['conditions'] = str(['ee7b7e6f-e904-4b4f-a5ec-b3bef040643e'])
my_df_sdp_entitlements_fw_update['conditionLinks'] = str([])
my_df_sdp_entitlements_fw_update['disabled'] = False
my_df_sdp_entitlements_fw_update['appShortcuts'] = str([])
my_df_sdp_entitlements_fw_update['appShortcutScripts'] = str([])

my_df_sdp_entitlements_actions_fw_update = my_df_proc_entitlements_actions_unique
# Replace unsupported characters on SDP
my_df_sdp_entitlements_actions_fw_update['name'] = (
    my_df_sdp_entitlements_actions_fw_update['name'].str.replace('/', '_', regex=False))
my_df_sdp_entitlements_actions_fw_update['name'] = (
    my_df_sdp_entitlements_actions_fw_update['name'].str.replace('(', '', regex=False))
my_df_sdp_entitlements_actions_fw_update['name'] = (
    my_df_sdp_entitlements_actions_fw_update['name'].str.replace(')', '', regex=False))
my_df_sdp_entitlements_actions_fw_update = my_df_sdp_entitlements_actions_fw_update.rename(
    columns={'name': 'ENTITLEMENT_name'}
)


# update my_df_sdp_build_entitlement
my_list_dfs = []
my_df_sdp_ents_wfw_updates = pd.concat([my_df_sdp_ents_wfw_updates, my_df_sdp_entitlements_fw_update])
my_list_dfs.append('my_df_sdp_ents_wfw_updates')

my_df_sdp_ents_actions_wfw_updates = pd.concat([my_df_sdp_ents_actions_wfw_updates,
                                                my_df_sdp_entitlements_actions_fw_update])
my_list_dfs.append('my_df_sdp_ents_actions_wfw_updates')

# %%

with pd.ExcelWriter(my_output_file_path_sdp_build, engine='xlsxwriter', ) as my_xls_file:
    print('Exporting Data Frames to:', my_output_file_path_sdp_build)
    for my_item_df_name in my_list_dfs:
        print(my_item_df_name)
        my_df_item = globals()[my_item_df_name]
        my_item_df_name = my_item_df_name.replace('my_df_', '')
        my_item_df_name = my_item_df_name.replace('ents', 'entitlements')
        my_item_df_name = my_item_df_name.replace('_wfw', '')
        my_item_df_name = my_item_df_name.replace('_updates', '')
        my_item_df_name = my_item_df_name.replace('sdp_', '')
        my_sheet_name = my_item_df_name
        my_df_item.to_excel(my_xls_file, sheet_name=my_sheet_name, startrow=1, header=False, index=False)
        workbook = my_xls_file.book
        worksheet = my_xls_file.sheets[my_sheet_name]
        (max_row, max_col) = my_df_item.shape
        column_settings = [{'header': column} for column in my_df_item.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
        worksheet.set_column(0, max_col - 1, 12)
