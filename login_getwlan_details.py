import requests
import json
import sys

session = requests.Session()
jar = requests.cookies.RequestsCookieJar()

baseurl = "https://general.direction.com:8443/wsg/api/public/v6_1/" #replace "general.direction.com" with either the host name or IP of a member of the cluster

# Written with 3.6.2 in mind

#http://docs.ruckuswireless.com/smartzone/3.6.2/sz100-public-api-reference-guide-3-6-2.html API documentation

sz_username = "" #Enter a username with read privages to everything you want to access
sz_password = "" #Password for the above account

headers_template = {'Content-Type': "application/json;charset=UTF-8"}

login_payload = '{  "username": "' + sz_username + '",\r\n  "password": "' + sz_password + '"}'

wlan_template_id = ""
zone_template_id = ""

def ruckus_post(url,data,headers = headers_template,check_cert = False):
    output = session.post(baseurl + url, data=data, headers=headers, verify=check_cert, cookies=jar)
    return output

get_login_session_cookie = ruckus_post("session",login_payload) #This uses the ruckus_post above to get a session valid session cookie into the cookie jar


def ruckus_get(url,headers = headers_template,check_cert = False):
    output = session.get(baseurl + url, headers=headers, verify=check_cert, cookies=jar)
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

# The below block will check if there is an assigned template if not then it will ask for a WLAN name and the Zone name and check if they exist.
# Below is ugly and needs rewiritng as a While statement
if wlan_template_id == "":
    wlan_template_name = input("Please enter a WLAN name to display the details of:")
    zone_template_name = input("Please enter the zone the WLAN is part of:")
    for row in cleaned_all_zone_wlan:
        if wlan_template_name == row[2] and zone_template_name == row[0]:
            print("Using {} from {} as the template.".format(wlan_template_name,zone_template_name))
            wlan_template_id = row[3]
            zone_template_id = row[1]
            break
        elif wlan_template_name[:4] in row[2] and zone_template_name == row[0]: #This will try and account for spelling mistakes in the WLAN name by offering a WLAN that matches with the first 3 charachers in the correct zone
            confirm = input("Did you mean {} from {}? Y/N".format(row[2],row[0]))
            if confirm.lower() == "y":
                wlan_template_id = row[3]
                zone_template_id = row[1]
                break
            else:
                sys.exit("WLAN name not found")

# Check to confirm we have an id for both the WLAN and it's zone before continuing and check the WLAN is actually in that zone it was entered directly
if wlan_template_id == "":
    sys.exit("No WLAN id")
if zone_template_id == "":
    sys.exit("No Zone id to use with the WLAN")

wlan_in_zone = False

for row in cleaned_all_zone_wlan:
    if zone_template_id == row[1] and wlan_template_id == row [3]:
        wlan_in_zone = True
        break

if wlan_in_zone != True:
    sys.exit("WLAN id not in Zone id")

# Below we are going to request the details of the WLAN selected

wlan_template_json = ruckus_get("rkszones/{}/wlans/{}".format(zone_template_id,wlan_template_id))

wlan_template = json.loads(wlan_template_json.text)

print(json.dumps(wlan_template, indent=4, sort_keys=True))
