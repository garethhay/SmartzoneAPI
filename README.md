# Ruckus SmartZone API

Repo for some basic python scripts for pulling data and printing data from Ruckus SmartZone's API.

Please note I am writing these as a training exercise for myself. Both new to python, git and it has been a long time since I have coded.

Tested against a SZ100 cluster of 2 running 3.6.2, please note these scripts will not work as is with vSZ-H only vSZ-E. Would recommend using a read-only account.

### Each script will need the below variables modifying for your own environment:

* `baseurl`
    * "https://general.direction.com:8443/wsg/api/public/v6_1/" #replace "general.direction.com" with either the host name or IP of a member of the cluster
* `szusername`
    * String
* `szpassword`
    * String

The API documentation is below for reference:

[Ruckus documentation for version 3.6.2](http://docs.ruckuswireless.com/smartzone/3.6.2/sz100-public-api-reference-guide-3-6-2.html)

## login_getzone.py

This will return all the configured zones on the cluster and print them out. At the end of the script you end up with a list of lists called `cleaned_zones`.

Format of the lists are:

`[name_of_zone,zone_id]`

## login_getwlans.py

This script builds on `login_getzone.py` to take the `cleaned_zones` list of lists and produce a list of lists called `cleaned_all_zone_wlan` that also includes the WLAN names and ids. Please note this is the WLAN name NOT the SSID.

Format of the lists are:

`[name_of_zone,zone_id,name_of_WLAN,WLAN_id]`
