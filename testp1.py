#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 20:01:25 2024

@author: chris
"""

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


""" 
/Users/chris/Library/CloudStorage/OneDrive-Personal/code_data/sonicwall/sonicwall_cfg_parsed/alv-irv-hq-fw-1_rules_current_20240217_192627.xlsx

my_input_file_path
#Load all sheets.   Get sheet names
my_dict_sheets  =  pd.read_excel(my_input_file_path, sheet_name=None).keys()
#my_df_sheets = pd.DataFrame(my_dict_sheets, columns=['SheetName'])
my_list_sheets = list(my_dict_sheets)

#read entitlement actions
my_df_entitlement = pd.read_excel(my_input_file_path, sheet_name='entitlements')
my_df_entitlement_actions = pd.read_excel(my_input_file_path, sheet_name='entitlements_actions')


sheet = FirewallPolicies
policySrcZone = ALV01_DMZ-SSLVPN
policySrcNet = ALV-LAS-CT-SSLVPN-1_
policyDstZone
policyDstNet Groups, Objects, and blanks (any)
policyDstSvc
policyName


AddressObjects
addrObjIdDisp
addrObjType
    1 = host
    2 = range
    4 = subnet
    8 = group
addrObjIp1
addrObjIp2

AddressObjectGroups
addro_grpToGrp
addro_atomToGrp


ServiceObjects
svcObjType
ServiceObjectGroups



"""
my_input_file_path = "/Users/chris/Library/CloudStorage/OneDrive-Personal/code_data/sonicwall/sonicwall_cfg_parsed/alv-irv-hq-fw-1_rules_current_20240217_192627.xlsx"

# Load all sheets
# Get sheet names
# Convert dict to list
my_dict_sheets = pd.read_excel(my_input_file_path, sheet_name=None).keys()
my_list_sheets = list(my_dict_sheets)

for my_sheet_item in my_list_sheets:
    globals()["my_df_" + my_sheet_item] = pd.read_excel(
        my_input_file_path, sheet_name=my_sheet_item
    )


my_df_fw_parsed = globals()["my_df_FirewallPolicies"][
    ["policyName", "policySrcNet", "policyDstZone", "policyDstNet", "policyDstSvc"]
]
my_df_fw_parsed = my_df_fw_parsed.fillna("ANY")
my_df_fw_parsed = my_df_fw_parsed[
    my_df_fw_parsed["policySrcNet"].str.contains("ALV-LAS-CT-SSLVPN-1_")
]


my_df_AddressObjects_parsed = globals()["my_df_AddressObjects"][
    ["addrObjIdDisp", "addrObjType", "addrObjIp1", "addrObjIp2"]
].copy()


my_df_AddressObjectGroups_parsed = globals()["my_df_AddressObjectGroups"][
    ["addro_grpToGrp", "addro_atomToGrp"]
].copy()
my_df_AddressObjectGroups_parsed.rename(
    columns={"addro_grpToGrp": "Group", "addro_atomToGrp": "GroupMember"}, inplace=True
)

#Not Needed
#my_df_AddressObjectGroups_parsed["GroupMemberAlsoGroup"] = ''
#my_df_AddressObjectGroups_parsed.loc[my_df_AddressObjectGroups_parsed["Group"].isin(my_df_AddressObjectGroups_parsed["GroupMember"]), "GroupMemberAlsoGroup"] = True

my_list_address_groups = list(my_df_AddressObjectGroups_parsed['Group'].unique())



def myf_convert_objects(my_row):
    if my_row["addrObjType"] == 1:
        my_value = my_row["addrObjIp1"]
    elif my_row["addrObjType"] == 2:
        my_value = my_row['addrObjIp1'] + "-" + my_row['addrObjIp2']
    elif my_row["addrObjType"] == 4:
        my_value = str(
            ipaddress.ip_network(
                my_row["addrObjIp1"] + "/" + my_row["addrObjIp2"], strict=False
            )
        )
    
    elif my_row["addrObjType"] == 8:
        my_value = "DO A GROUP FUNCTION"
    else:
        my_value = "SOMETHING IS BROKEN WRONG OBJ TYPE"
    return my_value


# Apply the function using .apply() and assign the result to a new column 'C'
my_df_AddressObjects_parsed["CustomHost"] = my_df_AddressObjects_parsed.apply(
    myf_convert_objects, axis=1
)


#join group to objects
my_df_a_merged = pd.merge(my_df_AddressObjectGroups_parsed, my_df_AddressObjects_parsed, how="outer", left_on="GroupMember", right_on="addrObjIdDisp")

my_df_b_merged = pd.merge(my_df_AddressObjectGroups_parsed, my_df_AddressObjects_parsed, how="outer", left_on="Group", right_on="addrObjIdDisp")

my_df_c_merged = my_df_a_merged


def myf_group_members(my_group):
    
    my_df_a = my_df_a_merged[my_df_a_merged['Group'] == my_group]
    
    my_list = []
    for my_row in my_df_a.itertuples():
        
        if my_row.addrObjType == 1:
            print(my_group, ' -- ', my_row.GroupMember,  ' -- ', my_row.CustomHost)
            my_list.append( my_row.CustomHost)
            
        elif my_row.addrObjType == 2:
            print(my_group, ' -- ', my_row.GroupMember,  ' -- ', my_row.CustomHost)
            my_list.append( my_row.CustomHost)
            
        elif my_row.addrObjType == 4:
            print(my_group, ' -- ', my_row.GroupMember,  ' -- ', my_row.CustomHost)
            my_list.append( my_row.CustomHost)
            
        elif my_row.addrObjType == 8:
            my_list.append(''.join(myf_group_members(my_row.addrObjIdDisp)))
            
        else:
            #Value is NAN so skip
            pass

        my_list = [value for value in my_list if value != ""]
    return my_list


for my_item_address_group in my_list_address_groups:
    print('---------------------')
    print(my_item_address_group) 
    #my_df_a = my_df_a_merged[my_df_a_merged['Group'] == my_item_address_group]
    #itter through rows.   Check if member is group via addrobject type.  If not group add to variable?
    my_group_members  = myf_group_members(my_item_address_group)
    print(my_item_address_group, ' ---- ', my_group_members)
    print('---------------------')
    # for my_row in my_df_a.itertuples():
    #     if my_row.addrObjType == 1:
    #         print(my_row.CustomHost)
    #     elif my_row.addrObjType == 2:
    #         print(my_row.CustomHost)
    #     elif my_row.addrObjType == 4:
    #         print(my_row.CustomHost)
    #     elif my_row.addrObjType == 8:
    #         myf_group_members(my_row.addrObjIdDisp)
    #     else:
    #         pass


# my_df_a_merged['CustomHost'] = my_df_a_merged['addrObjType' == 8].apply(
#    myf_group_members(my_df_a_merged['Group']), axis=1
# )

my_df_a_merged['CustomHost'] = my_df_a_merged.apply(lambda row:  myf_group_members(row['GroupMember']) if row['addrObjType'] == 8 else row['CustomHost'], axis=1)


my_df_b_merged['CustomHost'] = my_df_b_merged.apply(lambda row:  myf_group_members(row['addrObjIdDisp']) if row['addrObjType'] == 8 else row['CustomHost'], axis=1)


#Need to separate group to diff table

    #Fix group member also group
    #not itter rows correctly.  


#Need unique group list to for each against combined
#Not all groups are in add objects 
#Separate groups from address objects to create add objs and custom hosts
#Find group members from group members table
#Create new output of add objs custom hosts
#Compare groups vs address object type 8 groups
#need URLS

my_list_dfs = []
my_list_dfs.append('my_df_a_merged')
my_list_dfs.append('my_df_b_merged')



my_output_dir = '/Users/chris/OneDriveAlvakaNetworks/ALV01/DataAnalysis/Appgate/'
my_output_file_prefix = 'my_build_test_data'
my_output_file_extension = '.xlsx'

my_now = datetime.now()
my_timestamp = my_now.strftime('%Y%m%d_%H%M%S')
my_output_file_path = my_output_dir + my_output_file_prefix + '_' + my_output_file_extension
#my_output_file_path = my_output_dir + my_output_file_prefix + '_' + my_timestamp + my_output_file_extension
my_output_file_path_no_timestamp = my_output_dir + my_output_file_prefix + my_output_file_extension



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


#my_df_a_merged.to_csv('/Users/chris/OneDriveAlvakaNetworks/ALV01/DataAnalysis/Appgate/sample.csv', index=False) 