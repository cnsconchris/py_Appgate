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
my_input_file_dir = '/Users/chris/Library/CloudStorage/OneDrive-Personal/code_data/sonicwall/sonicwall_cfg_parsed/'
my_input_file = 'alv-las-ct-fw-1_rules_current_20240225_205133.xlsx'
my_input_file_path = my_input_file_dir + my_input_file

# Load all sheets
# Get sheet names
# Convert dict to list
my_list_sheets = list(pd.read_excel(my_input_file_path, sheet_name=None).keys())

# Loop through sheet names and create global dataframe for each sheet
for my_sheet_item in my_list_sheets:
    globals()['my_df_' + my_sheet_item] = pd.read_excel(
        my_input_file_path, sheet_name=my_sheet_item
    )

# Processed Firewall Policies = my_df_proc_fw_pol
my_df_proc_fw_pol = globals()['my_df_FirewallPolicies'][
    ['policyName', 'policySrcZone', 'policySrcNet', 'policyDstZone', 'policyDstNet', 'policyDstSvc']
]

# Change NAN entries to ANY
my_df_proc_fw_pol = my_df_proc_fw_pol.fillna('ANY')

# Processed Firewall Address Object Groups = my_df_proc_group_objects
my_df_proc_group_objects = globals()['my_df_AddressObjectGroups'][
    ['addro_grpToGrp', 'addro_atomToGrp']
].copy()

# Add addObjId as for matching against rules.
my_df_proc_group_objects['addrObjId'] = my_df_proc_group_objects['addro_grpToGrp']

# Rename columns
my_df_proc_group_objects.rename(
    columns={'addro_grpToGrp': 'Group', 'addro_atomToGrp': 'GroupMember'}, inplace=True
)

# Unique address object groups = my_df_proc_groups
my_df_proc_groups = pd.DataFrame()
my_df_proc_groups['AddressName'] = my_df_proc_group_objects['Group'].unique()

# Processed Firewall Address Objects = my_df_proc_address_objects
# Add addObjId as for matching against rules.
my_df_proc_address_objects = globals()['my_df_AddressObjects'][
    ['addrObjIdDisp', 'addrObjId', 'addrObjType', 'addrObjIp1', 'addrObjIp2']
].copy()

# Rename columns
my_df_proc_address_objects.rename(columns={'addrObjIdDisp': 'AddressName'}, inplace=True)

# Processed Firewall Address Objects FQDN = my_df_proc_address_objects_fqdn
my_df_proc_address_objects_fqdn = globals()['my_df_AddressObjectsFQDN'][
    ['addrObjFqdnId', 'addrObjFqdn']
].copy()

# Create new column and set all entries to FQDN for merge and matching with address objects.
# FQDN address objects imported into address combined = 99999
my_df_proc_address_objects_fqdn['addrObjType'] = 99999

# Add addObjId as for matching against rules.
my_df_proc_address_objects_fqdn['addrObjId'] = my_df_proc_address_objects_fqdn['addrObjFqdnId']

# Rename columns
my_df_proc_address_objects_fqdn.rename(columns={'addrObjFqdnId': 'AddressName'}, inplace=True)

# Combine my_df_proc_address_objects and my_df_proc_address_objects_fqdn = my_df_proc_address_combined
my_df_proc_address_combined = pd.concat(
    [my_df_proc_address_objects, my_df_proc_address_objects_fqdn], ignore_index=True)


# Compare and determine groups not in my_df_proc_address_combined and
# create my_df_proc_groups_not_in_proc_address_combined.
my_df_compare_temp = pd.merge(
    my_df_proc_address_combined, my_df_proc_groups, on='AddressName', how='outer', indicator=True)

my_df_proc_groups_not_in_proc_address_combined = my_df_compare_temp[
    ['AddressName']][my_df_compare_temp['_merge'] == 'right_only']

# Create new column and set all entries to GROUP for merge and matching with address objects.
# Groups imported from group list to addresses combined = 88888
my_df_proc_groups_not_in_proc_address_combined['addrObjType'] = 88888

# Add addObjId as for matching against rules.
my_df_proc_groups_not_in_proc_address_combined['addrObjId'] = my_df_proc_groups_not_in_proc_address_combined[
    'AddressName']

# Add groups not in my_df_proc_address_objects, my_df_proc_groups_not_in_proc_address_combined, into
# my_df_proc_address_objects.
my_df_proc_address_combined = pd.concat(
    [my_df_proc_address_combined, my_df_proc_groups_not_in_proc_address_combined], ignore_index=True)


# Function to convert to friendly output based on type into new row 'ProcessedAddress'.
def myf_convert_objects(my_row):
    if my_row['addrObjType'] == 1:
        my_value = my_row['addrObjIp1']
    elif my_row['addrObjType'] == 2:
        my_value = my_row['addrObjIp1'] + '-' + my_row['addrObjIp2']
    elif my_row['addrObjType'] == 4:
        my_value = str(
            ipaddress.ip_network(
                my_row['addrObjIp1'] + '/' + my_row['addrObjIp2'], strict=False
            )
        )
    elif my_row['addrObjType'] == 99999:
        my_value = my_row['addrObjFqdn']
    elif my_row['addrObjType'] == 8:
        my_value = 'GROUP'
    elif my_row['addrObjType'] == 88888:
        my_value = 'GROUP'
    else:
        my_value = 'SOMETHING IS BROKEN WRONG OBJ TYPE'
    return my_value


# Create new column ProcessedAddress and run function to apply.
my_df_proc_address_combined['ProcessedAddress'] = my_df_proc_address_combined.apply(myf_convert_objects, axis=1)


# Function to iterate through group objects, my_df_proc_group_objects, and combine each members' ProcessedAddress from
# my_df_proc_address_combined.
def myf_group_members(my_group):
    my_df_temp = my_df_proc_group_objects[my_df_proc_group_objects['Group'] == my_group]
    my_list = []
    for my_row in my_df_temp.itertuples():
        # print(my_row.Group, ' -- ', my_row.GroupMember)
        my_df_temp2 = my_df_proc_address_combined[my_df_proc_address_combined['addrObjId'] == my_row.GroupMember]
        for my_row2 in my_df_temp2.itertuples():
            if my_row2.addrObjType == 1:
                # print(my_group, ' -- ', my_row2.Address, ' -- ', my_row2.ProcessedAddress)
                my_list.append(my_row2.ProcessedAddress)

            elif my_row2.addrObjType == 2:
                # print(my_group, ' -- ', my_row2.Address, ' -- ', my_row2.ProcessedAddress)
                my_list.append(my_row2.ProcessedAddress)

            elif my_row2.addrObjType == 4:
                # print(my_group, ' -- ', my_row2.Address, ' -- ', my_row2.ProcessedAddress)
                my_list.append(my_row2.ProcessedAddress)

            elif my_row2.addrObjType == 99999:
                # print(my_group, ' -- ', my_row2.Address, ' -- ', my_row2.ProcessedAddress)
                my_list.append(my_row2.ProcessedAddress)

            elif my_row2.addrObjType == 8:
                # Flatten our groups of groups
                my_sub_list = myf_group_members(my_row2.AddressName)
                for my_sub_item in my_sub_list:
                    my_list.append(my_sub_item)
                # print('group in group')

            elif my_row2.addrObjType == 88888:
                # Flatten our groups of groups
                my_sub_list = myf_group_members(my_row2.AddressName)
                for my_sub_item in my_sub_list:
                    my_list.append(my_sub_item)
                # print('group in group')

            else:
                pass

    # Remove duplicates
    my_list = list(set(my_list))
    return my_list


# Process different object types variables to ProcessedAddress column
my_df_proc_address_combined['ProcessedAddress'] = my_df_proc_address_combined.apply(
    lambda row:  myf_group_members(row['addrObjId'])
    if row['addrObjType'] == 8 or row['addrObjType'] == 88888 else row['ProcessedAddress'], axis=1)


# Make sure all my_df_proc_address_combined['ProcessedAddress'] are lists
my_df_proc_address_combined['ProcessedAddress'] = my_df_proc_address_combined[
    'ProcessedAddress'] .apply(lambda x: x if isinstance(x, list) else [x])


# Function to match policy addresses to processed addresses.
def myf_process_pol_addresses(my_net):
    my_df_net = my_df_proc_address_combined[my_df_proc_address_combined['addrObjId'] == my_net]
    my_item_net = ''
    for my_row_net in my_df_net.itertuples():
        my_item_net = my_row_net.ProcessedAddress
        break

    return my_item_net


# Match firewall policy source addresses to address combined df.
my_df_proc_fw_pol['SrcProcessedAddress'] = my_df_proc_fw_pol.apply(
     lambda row:  myf_process_pol_addresses(
         row['policySrcNet']) if row['policySrcNet'] != 'ANY' else row['policySrcNet'], axis=1
 )

# Match firewall policy destination addresses to address combined df.
my_df_proc_fw_pol['DstProcessedAddress'] = my_df_proc_fw_pol.apply(
     lambda row:  myf_process_pol_addresses(
         row['policyDstNet']) if row['policyDstNet'] != 'ANY' else row['policyDstNet'], axis=1
 )

# Processed Firewall Policies VPN Specific = my_df_proc_fw_pol_vpn
my_df_proc_fw_pol_vpn = my_df_proc_fw_pol[my_df_proc_fw_pol['policySrcNet'].str.contains('ALV-LAS-CT-SSLVPN-1_')]

# Services parse
