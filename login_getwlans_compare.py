import requests
import json
import sys
from dictdiffer import diff

# Only use when testing, surpresses warnings about insecure servers
#from requests.packages.urllib3.exceptions import InsecureRequestWarning
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


session = requests.Session()
jar = requests.cookies.RequestsCookieJar()

baseurl = "https://general.direction.com:8443/wsg/api/public/v6_1/" #replace "general.direction.com" with either the host name or IP of a member of the cluster

# Written with 3.6.2 in mind

#http://docs.ruckuswireless.com/smartzone/3.6.2/sz100-public-api-reference-guide-3-6-2.html API documentation

sz_username = "" #Enter a username with read privages to everything you want to access
sz_password = "" #Password for the above account
check_cert = True # Change to false if using selfsigned certs or cert chain is not on the machine running the script

login_headers_template = {'Content-Type': "application/json;charset=UTF-8"}

login_payload = '{  "username": "' + sz_username + '",\r\n  "password": "' + sz_password + '"}'

wlan_template_id = ""
zone_template_id = ""

def ruckus_login(url,data):
    output = session.post(baseurl + url, data=data, headers=login_headers_template, verify=check_cert)
    return output
#This uses the ruckus_post above to get a session valid session cookie into the cookie jar
get_login_session_cookie = ruckus_login("session", login_payload)
jar = get_login_session_cookie.cookies

headers_template = {
                    'Content-Type': "application/json;charset=UTF-8",
                    'Cookie': 'JSESSIONID='+ jar['JSESSIONID']
                    }

def ruckus_post(url,data):
    output = session.post(baseurl + url, data=data, headers=headers_template, verify=check_cert)
    return output

def ruckus_get(url):
    output = session.get(baseurl + url, headers=headers_template, verify=check_cert)
    return output

    
jsonzones = ruckus_get("rkszones") #Get the JSON data for the zones confiured on the cluster

#The below function ruckus_list is used for stripping out the "list" dictionary from the returned JSON
def ruckus_list(jsondata):
    output = {}
    output = json.loads(jsondata.text)
    output = output["list"]
    return output

zones = ruckus_list(jsonzones)

def clean_ruckus_list(dictdata,dict_parent_name = "NONE",dict_parent_id = "NONE",names="name",ids="id"):
    output = []
    for row in dictdata:
        output_name = ""
        output_id = ""
        for key,val in row.items():
            if key == ids:
                output_id = row[key]
            elif key == names:
                output_name = row[key]
        if dict_parent_name and dict_parent_id == "NONE":
            output.append([output_name,output_id]) #Produce a list without useless data but catch if someone doesn't pass both arguements
        else:
            output.append([dict_parent_name,dict_parent_id,output_name,output_id])
    return output

cleaned_zones = clean_ruckus_list(zones)

cleaned_all_zone_wlan = []

for row in cleaned_zones:
    zone_id = row[1]
    zone_name = row[0]
    urltemplate = "rkszones/{}/wlans"
    jsonwlan = ruckus_get(urltemplate.format(zone_id))
    wlan = ruckus_list(jsonwlan)
    cleaned_all_zone_wlan.extend(clean_ruckus_list(wlan,zone_name,zone_id))


# Below is ugly and needs rewiritng as a While statement
# Get input, check input exists, if doesn't try first 4
def wlan_input():
    output = []
    zone_input_id = ""
    wlan_input_id = ""
    print('-' * 50)
    print('\n')
    wlan_input_name = input("Please enter a WLAN name : ")
    zone_input_name = input("Please enter the zone the WLAN is part of : ")
    print("-" * 5)
    wlan_input_name = wlan_input_name.lower()
    zone_input_name = zone_input_name.lower()
    tested = 0
    for row in cleaned_all_zone_wlan:
        tested += 1
        wlan_compare_input = row[2]
        zone_compare_input = row[0]
        wlan_compare_input = wlan_compare_input.lower()
        zone_compare_input = zone_compare_input.lower()
        if wlan_input_name == wlan_compare_input and zone_input_name == zone_compare_input:
            print("Using {} from {}.".format(wlan_input_name,zone_input_name))
            wlan_input_id = row[3]
            zone_input_id = row[1]
            output = zone_input_id, wlan_input_id, wlan_compare_input
            return output
        elif wlan_input_name[:4] in wlan_compare_input and zone_input_name == zone_compare_input:
            confirm = input("Did you mean {} from {}? Y/N : ".format(row[2],row[0]))
            if confirm.lower() == "y":
                wlan_input_id = row[3]
                zone_input_id = row[1]
                output = zone_input_id, wlan_input_id, wlan_compare_input
                return output
            else:
                sys.exit("WLAN name not found")
    sys.exit("Zone or WLAN name not found")

# Check to confirm we have an id for both the WLAN and it's zone before continuing and check
# the WLAN is actually in that zone it was entered directly
# Further checks due to possible assigned template
template_wlan_in_zone = False
if wlan_template_id == "" or zone_template_id =="":
    print('-' * 100)
    print('\n')
    print("For the template WLAN:")
    zone_template_id, wlan_template_id, wlan_template_name = wlan_input()
else:
    for row in cleaned_all_zone_wlan:
        if zone_template_id == row[1] and wlan_template_id == row [3]:
            template_wlan_in_zone = True
            break
        else:
            if template_wlan_in_zone != True:
                sys.exit("WLAN id not in Zone id")
            elif wlan_template_id == "":
                sys.exit("No WLAN id")
            elif zone_template_id == "":
                sys.exit("No Zone id to use with the WLAN")

# Get the second WLAN and Zone id
print("\n")
print("For the comparison WLAN:")
zone_comparison_id, wlan_comparison_id, wlan_comparison_name = wlan_input()
print("\n")
print("-" * 100)
#Do the get and JSON.loads to receive both WLAN details
wlan_template_json = ruckus_get("rkszones/{}/wlans/{}".format( zone_template_id, wlan_template_id))
wlan_comparison_json = ruckus_get("rkszones/{}/wlans/{}".format( zone_comparison_id, wlan_comparison_id))

wlan_template = json.loads(wlan_template_json.text)
wlan_comparison = json.loads(wlan_comparison_json.text)

ignore_list = ['id', 'name', 'ssid', 'encryption.passphrase', 'bssid', 'zoneId', 'description']

#use diff to return a list of tuples with the differences between the two WLANs
wlans_compared = diff( wlan_template, wlan_comparison, ignore = ignore_list)

print("\n")
print("The differences between '{}' and '{}' are:".format( wlan_template_name, wlan_comparison_name))
print("\n")
for row in wlans_compared:
    print("Type: {} | Where: {} | What: {}".format( row[0], row[1], row[2]))
    print("-" * 5)
print("\n")
print("-" * 100)
