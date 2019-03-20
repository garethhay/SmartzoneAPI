import requests
import json

session = requests.Session()
jar = requests.cookies.RequestsCookieJar()

baseurl = "https://general.direction.com:8443/wsg/api/public/v6_1/" #replace "general.direction.com" with either the host name or IP of a member of the cluster

# Written with 3.6.2 in mind

#http://docs.ruckuswireless.com/smartzone/3.6.2/sz100-public-api-reference-guide-3-6-2.html API documentation

szusername = "" #Enter a username with read privages to everything you want to access
szpassword = "" #Password for the above account

headers_template = {'Content-Type': "application/json;charset=UTF-8"}

loginpayload = '{  "username": "' + szusername + '",\r\n  "password": "' + szpassword + '"}'


def ruckus_post(url,data,headers = headers_template,check_cert = False):
    output = session.post(baseurl + url, data=data, headers=headers, verify=check_cert, cookies=jar)
    return output

get_login_session_cookie = ruckus_post("session",loginpayload) #This uses the ruckus_post above to get a session valid session cookie into the cookie jar


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

print("\n")
print("-" * 50)
print("\n")
print("The WLANs configured on this szcluster are:")
print("\n")
zone_print = ""
for row in cleaned_all_zone_wlan:
    if zone_print == row[0]:
        print("    Name: {} and ID: {}".format(row[2],row[3]))
    else:
        zone_print = row[0]
        print("-" * 5)
        print("\n")
        print("{} zone's WLAN are:".format(row[0]))
        print("\n")
        print("    Name: {} and ID: {}".format(row[2],row[3]))
print("\n")
print("-" * 50)
