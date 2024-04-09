# %%

from itertools import islice
import pandas as pd
import re
from datetime import datetime
import base64
import xlsxwriter
import ipaddress
import sqlite3
from sqlalchemy import create_engine


# v.2 Adds decode and excel formatting
# v.3 Removed decode encrypted file.  Change of input and output standard dirs. Decode is a now a separate script.
# v.4 Combined with processing rules scripts.  Writes to DB
# v.4a Adds straight from decryption file
# v.5 MariaDB. Fix globals()['my_df_AddressObjectsFQDN'] being empty. Example
# MSSQL Example
#


# Future scripts need to check for empty dataframes.


my_enc_input_dir = '/Users/chris/Library/CloudStorage/OneDrive-Personal/code_data/sonicwall/sonicwall_cfg_encrypted/'
my_enc_input_file = 'alv-irv-hq-fw-1_20240401.exp'
my_enc_input_path = my_enc_input_dir + my_enc_input_file
print(my_enc_input_path)

# Decode file
my_enc_file = open(my_enc_input_path, "r")
my_enc_content = my_enc_file.read()
my_dec_bytes = base64.b64decode(my_enc_content)
# my_dec_content = my_dec_bytes.decode('ascii')  # .replace('&', '\n').encode()
my_dec_content = my_dec_bytes.decode('ascii').split('&')
my_df_decrypted_config = pd.DataFrame({'CONFIG_DATA': my_dec_content})


my_fw_name = 'ALV-IRV-HQ-FW-1'


# Check output name
my_db_dir = '/Users/chris/Library/CloudStorage/OneDrive-Personal/code_data/sonicwall/'
my_db_file_prefix = 'sonicwall_test'
my_db_file_extension = '.db'


my_now = datetime.now()
my_timestamp = my_now.strftime("%Y%m%d_%H%M%S")

# my_db_path = my_db_dir + my_db_file_prefix + my_timestamp + my_db_file_extension
my_db_path = my_db_dir + my_db_file_prefix + my_db_file_extension


my_config_line_number = 0
my_config_count = 0

my_config_start = 'policyAction_'
my_config_end = 'policyPdfObject_'

my_config_get_dict = {
    'FirewallPolicies': {'Start': 'policyAction_', 'End': 'policyPdfObject_'},
    'AddressObjects': {'Start': 'addrObjId_', 'End': 'addrObjInstanceId_'},
    'AddressObjectsIPV6': {'Start': 'addrObjV6Id_', 'End': 'addrObjV6InstanceId_'},
    'AddressObjectsFQDN': {'Start': 'addrObjFqdnId_', 'End': 'addrObjFqdnManualTTLSetting_'},
    'AddressObjectGroups': {'Start': 'addro_atomToGrp_', 'End': 'addro_grpToGrp_'},
    'ServiceObjects': {'Start': 'svcObjId_', 'End': 'svcObjHigherPrecedence_'},
    'ServiceObjectGroups': {'Start': 'so_atomToGrp_', 'End': 'so_grpToGrp'},
    'NATPolicies': {'Start': 'natPolicyOrigSrc_', 'End': 'natPolicyTimeLastHit_'},
    'Interfaces': {'Start': 'iface_ifnum_', 'End': 'iface_tunnel_id_'},
    'Zones': {'Start': 'zoneObjId_', 'End': 'zoneObjPortalRadSkipDigest_'}
}


# Function to autocorrect value type
# def autocorrect_value(value):
#     try:
#         # Try converting to integer
#         return int(value)
#     except ValueError:
#         try:
#             # Try converting to float
#             return float(value)
#         except ValueError:
#             # If conversion fails, return the original value
#             return value
def autocorrect_value(value):
    try:
        # Try converting to integer
        return int(value)
    except ValueError:
        try:
            # Try converting to Str
            return str(value)
        except ValueError:
            # If conversion fails, return the original value
            return value

my_collect_data = False
my_table_dict = {}

for my_config_get_dict_key in my_config_get_dict.keys():
    globals()['my_table_dict_' + my_config_get_dict_key] = {}


for my_config_line in my_df_decrypted_config['CONFIG_DATA']:
    my_config_line_number += 1
    my_config_line = my_config_line.replace('%20', ' ')
    my_config_line = my_config_line.replace('%26', '&')
    my_config_line = my_config_line.replace('%3a', ':')
    # if my_config_line_number >= 29537:
    #     print('BOOM - Breaking It')
    #     break

    for my_config_key, my_config_value in my_config_get_dict.items():
        # Loop thru config type on each line
        my_config_start = my_config_value['Start']
        my_config_end = my_config_value['End']

        if my_config_line.startswith(my_config_start):
            my_config_line_stripped = my_config_line.strip()
            my_config_line_split = my_config_line_stripped.split("=")
            my_config_line_header = my_config_line_split[0].rsplit("_", 1)
            my_config_line_header_name = my_config_line_header[0]
            my_config_line_header_id = my_config_line_header[1]
            my_config_line_value = my_config_line_split[1]
            my_collect_data = True
            my_row_dict = {}
            my_row_dict['PolicyID'] = my_config_line_header_id
            my_row_dict[my_config_line_header_name] = my_config_line_value

        elif my_config_line.startswith(my_config_end):
            my_config_line_stripped = my_config_line.strip()
            my_config_line_split = my_config_line_stripped.split("=")
            my_config_line_header = my_config_line_split[0].rsplit("_", 1)
            my_config_line_header_name = my_config_line_header[0]
            my_config_line_header_id = my_config_line_header[1]
            my_config_line_value = my_config_line_split[1]
            my_row_dict[my_config_line_header_name] = my_config_line_value
            my_table_dict['PolicyID:' + str(my_config_line_header_id)] = my_row_dict
            globals()['my_table_dict_' + my_config_key]['PolicyID:' + str(my_config_line_header_id)] = my_row_dict
            my_collect_data = False

        elif my_collect_data == True:
            my_config_line_stripped = my_config_line.strip()
            my_config_line_split = my_config_line_stripped.split("=")
            my_config_line_header = my_config_line_split[0].rsplit("_", 1)
            my_config_line_header_name = my_config_line_header[0]
            my_config_line_header_id = my_config_line_header[1]
            my_config_line_value = my_config_line_split[1]
            my_row_dict[my_config_line_header_name] = my_config_line_value
            my_row_dict[my_config_line_header_name] = autocorrect_value(my_config_line_value)

for my_table_name in my_config_get_dict.keys():
    globals()['my_df_' + my_table_name] = (
        pd.DataFrame.from_dict(globals()['my_table_dict_' + my_table_name], orient='index').reset_index(drop=True))

# Processed Firewall Policies = my_df_proc_fw_pol
my_df_proc_fw_pol = globals()['my_df_FirewallPolicies'][
    ['policyName', 'policyComment', 'policyAction', 'policySrcZone', 'policySrcNet',
     'policySrcSvc', 'policyDstZone', 'policyDstNet', 'policyDstSvc']
]

# Change NAN entries to ANY
my_df_proc_fw_pol = my_df_proc_fw_pol.fillna('ANY')


# Function to convert Policy Action to readable.
def myf_process_pol_action(my_pol_action_input):
    my_pol_action_output = ''
    if my_pol_action_input == 0:
        my_pol_action_output = 'DENY'
    elif my_pol_action_input == 1:
        my_pol_action_output = 'DISCARD'
    elif my_pol_action_input == 2:
        my_pol_action_output = 'ALLOW'
    else:
        pass

    return my_pol_action_output


# Convert Policy Action to readable with function.
my_df_proc_fw_pol['policyAction'] = my_df_proc_fw_pol['policyAction'].apply(myf_process_pol_action)

# Processed Firewall Address Object Groups = my_df_proc_address_object_groups
my_df_proc_address_object_groups = globals()['my_df_AddressObjectGroups'][
    ['addro_grpToGrp', 'addro_atomToGrp']
].copy()

# Add addObjId as for matching against rules.
my_df_proc_address_object_groups['addrObjId'] = my_df_proc_address_object_groups['addro_grpToGrp']

# Rename columns
my_df_proc_address_object_groups.rename(
    columns={'addro_grpToGrp': 'Group', 'addro_atomToGrp': 'GroupMember'}, inplace=True
)

# Unique address object groups = my_df_proc_address_groups
my_df_proc_address_groups = pd.DataFrame()
my_df_proc_address_groups['AddressName'] = my_df_proc_address_object_groups['Group'].unique()

# Processed Firewall Address Objects = my_df_proc_address_objects
# Add addObjId as for matching against rules.
my_df_proc_address_objects = globals()['my_df_AddressObjects'][
    ['addrObjIdDisp', 'addrObjId', 'addrObjType', 'addrObjIp1', 'addrObjIp2']
].copy()

# Rename columns
my_df_proc_address_objects.rename(columns={'addrObjIdDisp': 'AddressName'}, inplace=True)

# Add column names to empty globals()['my_df_AddressObjectsFQDN']
# Processed Firewall Address Objects FQDN = my_df_proc_address_objects_fqdn
if not globals()['my_df_AddressObjectsFQDN'].empty:
    my_df_proc_address_objects_fqdn = globals()['my_df_AddressObjectsFQDN'][
        ['addrObjFqdnId', 'addrObjFqdn']
    ].copy()
else:
    my_df_proc_address_objects_fqdn = pd.DataFrame(columns=['addrObjFqdnId', 'addrObjFqdn'])
    globals()['my_df_AddressObjectsFQDN'] = pd.DataFrame(columns=['addrObjFqdnId', 'addrObjFqdn'])

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
# create my_df_proc_address_groups_not_in_proc_address_combined.
my_df_compare_temp = pd.merge(
    my_df_proc_address_combined, my_df_proc_address_groups, on='AddressName', how='outer', indicator=True)

my_df_proc_address_groups_not_in_proc_address_combined = my_df_compare_temp[
    ['AddressName']][my_df_compare_temp['_merge'] == 'right_only']

# Create new column and set all entries to GROUP for merge and matching with address objects.
# Groups imported from group list to addresses combined = 88888
my_df_proc_address_groups_not_in_proc_address_combined['addrObjType'] = 88888

# Add addObjId as for matching against rules.
my_df_proc_address_groups_not_in_proc_address_combined['addrObjId'] = (
    my_df_proc_address_groups_not_in_proc_address_combined)['AddressName']

# Add groups not in my_df_proc_address_objects, my_df_proc_address_groups_not_in_proc_address_combined, into
# my_df_proc_address_objects.
my_df_proc_address_combined = pd.concat(
    [my_df_proc_address_combined, my_df_proc_address_groups_not_in_proc_address_combined], ignore_index=True)


# addrObjType
#     1 = host
#     2 = range
#     4 = subnet
#     8 = group


# Function to convert to friendly output based on type into new row 'ProcessedAddress'.
def myf_convert_objects(my_row):
    if my_row['addrObjType'] == 1:
        my_value = my_row['addrObjIp1']
    elif my_row['addrObjType'] == 2:
        # my_value = my_row['addrObjIp1'] + '-' + my_row['addrObjIp2']
        my_fvar_start = ipaddress.IPv4Address(my_row['addrObjIp1'])
        my_fvar_end = ipaddress.IPv4Address(my_row['addrObjIp2'])
        my_fvar_ip_list = [str(ipaddress.IPv4Address(ip)) for ip in range(int(my_fvar_start), int(my_fvar_end) + 1)]
        my_value = my_fvar_ip_list
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


# Function to iterate through group objects, my_df_proc_address_object_groups,
# and combine each members' ProcessedAddress from my_df_proc_address_combined.
def myf_group_members(my_group):
    my_df_temp = my_df_proc_address_object_groups[my_df_proc_address_object_groups['Group'] == my_group]
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
    lambda row: myf_group_members(row['addrObjId'])
    if row['addrObjType'] == 8 or row['addrObjType'] == 88888 else row['ProcessedAddress'], axis=1)

# Make sure all my_df_proc_address_combined['ProcessedAddress'] are lists for formatting.
my_df_proc_address_combined['ProcessedAddress'] = my_df_proc_address_combined[
    'ProcessedAddress'].apply(lambda x: x if isinstance(x, list) else [x])

# Make then convert list in my_df_proc_address_combined['ProcessedAddress'] to string
my_df_proc_address_combined['ProcessedAddress'] = my_df_proc_address_combined['ProcessedAddress'].astype(str)


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
    lambda row: myf_process_pol_addresses(
        row['policySrcNet']) if row['policySrcNet'] != 'ANY' else row['policySrcNet'], axis=1
)

# Match firewall policy destination addresses to address combined df.
my_df_proc_fw_pol['DstProcessedAddress'] = my_df_proc_fw_pol.apply(
    lambda row: myf_process_pol_addresses(
        row['policyDstNet']) if row['policyDstNet'] != 'ANY' else row['policyDstNet'], axis=1
)

# Services processing
# Processed Firewall Service Objects = my_df_proc_service_objects
# Add addObjId as for matching against rules.
my_df_proc_service_objects = globals()['my_df_ServiceObjects'][
    ['svcObjId', 'svcObjType', 'svcObjIpType', 'svcObjPort1', 'svcObjPort2']
].copy()

# Rename columns
my_df_proc_service_objects.rename(columns={'svcObjId': 'ServiceName'}, inplace=True)

# Processed Firewall Service Object Groups = my_df_proc_service_object_group
my_df_proc_service_object_groups = globals()['my_df_ServiceObjectGroups'][
    ['so_grpToGrp', 'so_atomToGrp']
].copy()

# Create my_df_proc_service_combined.
my_df_proc_service_combined = my_df_proc_service_objects

# Rename columns
my_df_proc_service_object_groups.rename(
    columns={'so_grpToGrp': 'Group', 'so_atomToGrp': 'GroupMember'}, inplace=True
)

# Unique service object groups = my_df_proc_service_groups
my_df_proc_service_groups = pd.DataFrame()
my_df_proc_service_groups['ServiceName'] = my_df_proc_service_object_groups['Group'].unique()

# Compare and determine groups not in my_df_proc_service_combined and
# create my_df_proc_service_groups_not_in_proc_service_combined.
my_df_service_compare_temp = pd.merge(
    my_df_proc_service_combined, my_df_proc_service_groups, on='ServiceName', how='outer', indicator=True)


# No issues like the address groups.  This can be ignored.
# my_df_proc_service_groups_not_in_proc_address_combined = my_df_service_compare_temp[
#     ['ServiceName']][my_df_service_compare_temp['_merge'] == 'right_only']


# Function to convert to friendly output based on type into new row 'ProcessedService'.
# svcObjType:
#     1 = SVC
#     2 = GROUP
# svcObjIpType:
#     1 = ICMP
#     6 = TCP
#     17 = UDP
#     41 = 6over4
#     47 = GRE
#     50 = IPSEC_ESP
#     58 = ICMPv6
#     108 = IPCOMP
def myf_convert_service_objects(my_row):
    my_value_1 = 'NA'
    if my_row['svcObjType'] == 2:
        my_value = 'GROUP'
    elif my_row['svcObjType'] == 1:
        if my_row['svcObjPort1'] == my_row['svcObjPort2']:
            my_value = str(my_row['svcObjPort1'])
        else:
            my_value = str(my_row['svcObjPort1']) + '-' + str(my_row['svcObjPort2'])
        if my_row['svcObjIpType'] == 1:
            my_value_1 = 'ICMP'
        elif my_row['svcObjIpType'] == 6:
            my_value_1 = 'TCP'
        elif my_row['svcObjIpType'] == 17:
            my_value_1 = 'UDP'
        elif my_row['svcObjIpType'] == 41:
            my_value_1 = '6over4'
        elif my_row['svcObjIpType'] == 47:
            my_value_1 = 'GRE'
        elif my_row['svcObjIpType'] == 50:
            my_value_1 = 'IPSEC_ESP'
        elif my_row['svcObjIpType'] == 58:
            my_value_1 = 'ICMPv6'
        elif my_row['svcObjIpType'] == 108:
            my_value_1 = 'IPCOMP'
        else:
            pass
    else:
        my_value = 'SOMETHING IS BROKEN WRONG OBJ TYPE'

    return my_value_1, my_value


# Create Protocol and Service Type columns
my_df_proc_service_combined['ProcessedProto'], my_df_proc_service_combined[
    'ProcessedService'] = zip(*my_df_proc_service_combined.apply(myf_convert_service_objects, axis=1))


# Function to get svc group members and nonmembers with protocol and ports.
def myf_get_service_values(my_svc_input):
    my_df_svc_info = pd.DataFrame(columns=['service', 'type', 'ports'])

    # Iterate through group members of group list.
    my_df_group_members = my_df_proc_service_object_groups[my_df_proc_service_object_groups['Group'] == my_svc_input]

    # If service is not in a group get type and ports.
    if my_df_group_members.empty:
        my_df_group_member_info = my_df_proc_service_combined[my_df_proc_service_combined[
                                                                  'ServiceName'] == my_svc_input]

        for my_row_member_info in my_df_group_member_info.itertuples():
            if my_row_member_info.svcObjType == 1:
                my_service = my_row_member_info.ServiceName
                my_ports = my_row_member_info.ProcessedService
                if my_row_member_info.svcObjIpType == 1:
                    my_type = 'icmp'
                elif my_row_member_info.svcObjIpType == 6:
                    my_type = 'tcp'
                elif my_row_member_info.svcObjIpType == 17:
                    my_type = 'udp'
                elif my_row_member_info.svcObjIpType == 41:
                    my_type = '6over4'
                elif my_row_member_info.svcObjIpType == 47:
                    my_type = 'gre'
                elif my_row_member_info.svcObjIpType == 50:
                    my_type = 'ipsec_esp'
                elif my_row_member_info.svcObjIpType == 58:
                    my_type = 'icmpv6'
                elif my_row_member_info.svcObjIpType == 108:
                    my_type = 'ipcomp'
                else:
                    my_type = 'na'
                    my_ports = 'na'

                my_df_svc_row = pd.DataFrame({'service': [my_service], 'type': [my_type], 'ports': [my_ports]})

                my_df_svc_info = pd.concat([my_df_svc_info, my_df_svc_row])

    # If service is in a group get type and ports and check to see if it has groups inside of it.
    else:
        for my_row_member in my_df_group_members.itertuples():

            my_df_group_member_info = my_df_proc_service_combined[my_df_proc_service_combined[
                                                                      'ServiceName'] == my_row_member.GroupMember]

            for my_row_member_info in my_df_group_member_info.itertuples():
                if my_row_member_info.svcObjType == 1:
                    my_service = my_row_member_info.ServiceName
                    my_ports = my_row_member_info.ProcessedService
                    if my_row_member_info.svcObjIpType == 1:
                        my_type = 'icmp'
                    elif my_row_member_info.svcObjIpType == 6:
                        my_type = 'tcp'
                    elif my_row_member_info.svcObjIpType == 17:
                        my_type = 'udp'
                    elif my_row_member_info.svcObjIpType == 41:
                        my_type = '6over4'
                    elif my_row_member_info.svcObjIpType == 47:
                        my_type = 'gre'
                    elif my_row_member_info.svcObjIpType == 50:
                        my_type = 'ipsec_esp'
                    elif my_row_member_info.svcObjIpType == 58:
                        my_type = 'icmpv6'
                    elif my_row_member_info.svcObjIpType == 108:
                        my_type = 'ipcomp'
                    else:
                        my_type = 'na'
                        my_ports = 'na'

                    my_df_svc_row = pd.DataFrame({'service': [my_service], 'type': [my_type], 'ports': [my_ports]})
                    my_df_svc_info = pd.concat([my_df_svc_info, my_df_svc_row])

                # Process group inside of groups
                elif my_row_member_info.svcObjType == 2:
                    my_df_sub_svc_info = myf_get_service_values(my_row_member_info.ServiceName)
                    my_df_svc_info = pd.concat([my_df_svc_info, my_df_sub_svc_info])

    return my_df_svc_info


# Update my_df_proc_service_combined with dictionary of service protocols and ports
my_df_proc_service_combined['DictProcessedService'] = my_df_proc_service_combined.apply(
    lambda row: myf_get_service_values(row['ServiceName']).to_dict(orient='records'), axis=1)

# Create combined values dict for Appgate API.
my_df_proc_service_combined['GroupedDictService'] = my_df_proc_service_combined.apply(
    lambda row: myf_get_service_values(
        row['ServiceName']).drop_duplicates(subset=['type', 'ports']).groupby('type', group_keys=True)['ports'].apply(
        list).reset_index().to_dict(orient='records'), axis=1)


# Function to match policy services to dict processed services.
def myf_process_pol_services(my_svc):
    my_df_svc = my_df_proc_service_combined[my_df_proc_service_combined['ServiceName'] == my_svc]
    my_item_svc = ''
    for my_row_svc in my_df_svc.itertuples():
        my_item_svc = my_row_svc.DictProcessedService
        break

    return my_item_svc


# Make column and run function to match firewall policy destination service to service combined service df.
my_df_proc_fw_pol['DstDictProcessedService'] = my_df_proc_fw_pol.apply(
    lambda row: myf_process_pol_services(
        row['policyDstSvc']) if row['policyDstSvc'] != 'ANY' else row['policyDstSvc'], axis=1
)


# Function to match policy services to grouped dict processed services for Appgate API.
def myf_process_pol_grouped_dict_services(my_svc):
    my_df_svc = my_df_proc_service_combined[my_df_proc_service_combined['ServiceName'] == my_svc]
    my_item_svc = ''
    for my_row_svc in my_df_svc.itertuples():
        my_item_svc = my_row_svc.GroupedDictService
        break

    return my_item_svc


# Make column and run function to match firewall policy destination service to
# service combined service df dict processed services for Appgate API.
my_df_proc_fw_pol['DstGroupedDictService'] = my_df_proc_fw_pol.apply(
    lambda row: myf_process_pol_grouped_dict_services(
        row['policyDstSvc']) if row['policyDstSvc'] != 'ANY' else row['policyDstSvc'], axis=1
)

# Processed Firewall Policies VPN Specific = my_df_proc_fw_pol_vpn
# my_df_proc_fw_pol_vpn = my_df_proc_fw_pol[
#     my_df_proc_fw_pol['policySrcNet'].str.contains('ALV-LAS-CT-SSLVPN-1_')
#     | my_df_proc_fw_pol['policySrcNet'].str.contains('ALV-LAS-CT-SDP-IP-POOL')]

# List of dataframes to export to excel.
my_list_dataframes = ['my_df_AddressObjectGroups', 'my_df_AddressObjects', 'my_df_AddressObjectsFQDN',
                      'my_df_AddressObjectsIPV6', 'my_df_FirewallPolicies', 'my_df_Interfaces', 'my_df_NATPolicies',
                      'my_df_ServiceObjectGroups', 'my_df_ServiceObjects', 'my_df_Zones', 'my_df_compare_temp',
                      'my_df_proc_address_combined', 'my_df_proc_address_groups',
                      'my_df_proc_address_object_groups',
                      'my_df_proc_address_objects', 'my_df_proc_address_objects_fqdn', 'my_df_proc_fw_pol',
                      'my_df_proc_service_combined', 'my_df_proc_service_groups',
                      'my_df_proc_service_object_groups', 'my_df_proc_service_objects', 'my_df_service_compare_temp',
                      'my_df_decrypted_config']

# Need to convert large 64int to string due to SQL limitations
globals()['my_df_AddressObjects']['addrObjInstanceId'] \
    = globals()['my_df_AddressObjects']['addrObjInstanceId'].astype(str)
globals()['my_df_AddressObjectsIPV6']['addrObjV6InstanceId'] \
    = globals()['my_df_AddressObjectsIPV6']['addrObjV6InstanceId'].astype(str)

globals()['my_df_FirewallPolicies']['policyInstanceId']\
    = globals()['my_df_FirewallPolicies']['policyInstanceId'].astype(str)
globals()['my_df_FirewallPolicies']['perPolicyGeoIpBitmap']\
    = globals()['my_df_FirewallPolicies']['perPolicyGeoIpBitmap'].astype(str)

globals()['my_df_NATPolicies']['natPolicyInstanceId'] \
    = globals()['my_df_NATPolicies']['natPolicyInstanceId'].astype(str)
globals()['my_df_ServiceObjects']['svcObjInstanceId'] \
    = globals()['my_df_ServiceObjects']['svcObjInstanceId'].astype(str)
globals()['my_df_Zones']['zoneObjInstanceId'] \
    = globals()['my_df_Zones']['zoneObjInstanceId'].astype(str)
globals()['my_df_proc_fw_pol']['DstProcessedAddress'] \
    = globals()['my_df_proc_fw_pol']['SrcProcessedAddress'].astype(str)
globals()['my_df_proc_fw_pol']['SrcProcessedAddress'] \
    = globals()['my_df_proc_fw_pol']['DstProcessedAddress'].astype(str)
globals()['my_df_proc_fw_pol']['DstDictProcessedService'] \
    = globals()['my_df_proc_fw_pol']['DstDictProcessedService'].astype(str)
globals()['my_df_proc_fw_pol']['DstGroupedDictService'] \
    = globals()['my_df_proc_fw_pol']['DstGroupedDictService'].astype(str)
globals()['my_df_proc_service_combined']['DictProcessedService'] \
    = globals()['my_df_proc_service_combined']['DictProcessedService'].astype(str)
globals()['my_df_proc_service_combined']['GroupedDictService'] \
    = globals()['my_df_proc_service_combined']['GroupedDictService'].astype(str)

# conn = sqlite3.connect(my_db_path)

#engine = create_engine('mysql+mysqlconnector://admin:IlikemyMDB!321@stan.home.cnscon.com:3306/sonicwall_configs')

server = 'ALV-LASDBDEV01INST01.alvaka.net'
database = 'alv_sonicwall_configuration'
username = '<SQL Server Username>'
password = '<SQL Server Password>'
# engine = create_engine(
# f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')
engine = create_engine(
    f'mssql+pyodbc://@{server}/{database}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')


for my_item_df_name in my_list_dataframes:
    print(my_item_df_name)
    my_df_item = globals()[my_item_df_name]
    my_table_name = my_fw_name + '_' + my_item_df_name.replace('my_df_', '')
    # my_df_item.to_sql(my_table_name, conn, if_exists='replace')
    my_df_item.to_sql(name=my_table_name, con=engine, if_exists='replace', index=False)

# Check for writing back out of lists from string.
#con.close()

print('done')


