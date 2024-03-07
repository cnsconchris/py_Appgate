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


''' 
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



'''



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



# %%
# with pd.ExcelWriter(my_output_file_path, engine='xlsxwriter') as my_xls_file:
#     print('Exporting Data Frames to:', my_output_file_path)
#     for my_item_df_name in my_list_dfs:
#         print(my_item_df_name)
#         my_df_item = globals()[my_item_df_name]
#         my_sheet_name = my_item_df_name.replace('my_df_','')
#         my_df_item.to_excel(my_xls_file, sheet_name=my_sheet_name, startrow=1, header=False, index=False)
#         workbook = my_xls_file.book
#         worksheet = my_xls_file.sheets[my_sheet_name]
#         (max_row, max_col) = my_df_item.shape
#         column_settings = [{'header': column} for column in my_df_item.columns]
#         worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
#         worksheet.set_column(0, max_col - 1, 12)


#my_df_a_merged.to_csv('/Users/chris/OneDriveAlvakaNetworks/ALV01/DataAnalysis/Appgate/sample.csv', index=False) 