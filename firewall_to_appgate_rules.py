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
my_df_AddressObjectGroups_parsed["GroupMemberAlsoGroup"] = ''
my_df_AddressObjectGroups_parsed.loc[my_df_AddressObjectGroups_parsed["Group"].isin(my_df_AddressObjectGroups_parsed["GroupMember"]), "GroupMemberAlsoGroup"] = True

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


for my_item_address_group in my_list_address_groups:
    #print(my_item_address_group)
    my_df_a = my_df_a_merged[my_df_a_merged['Group'] == my_item_address_group]
    #itter through rows.   Check if member is group via addrobject type.  If not group add to variable?

