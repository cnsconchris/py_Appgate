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


my_input_file_dir = '/Users/chris/OneDriveAlvakaNetworks/ALV01/DataAnalysis/Appgate/'
my_input_file = 'alv-las-ct-corefw-1_rules_current_20240311_220713_more_20240316_002557.xlsx'
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