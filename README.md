# Ruckus SmartZone API

Repo for some basic python scripts for pulling and printing data from Ruckus SmartZone's API.

Please note the following:
I am new to both python and git. I am writing these as a training exercise for myself and I have not written code for an extended period.
I have tested this against a SZ100 cluster of 2 running 3.6.2. These scripts will not work in the current state with vSZ-H and will only work correctly with vSZ-E. I would recommend using a read-only account.

### Each script will need the following variables which will need modifing for your own configuration:

* `baseurl`
    * "https://general.direction.com:8443/wsg/api/public/v6_1/" #replace "general.direction.com" with either the host name or IP of a member of the cluster
* `szusername`
    * String
* `szpassword`
    * String

The API documentation is below for reference:

[Ruckus documentation for version 3.6.2](http://docs.ruckuswireless.com/smartzone/3.6.2/sz100-public-api-reference-guide-3-6-2.html)

## login_getzone.py

This will return all the configured zones on the cluster and print them out. The script will output a list of lists called `cleaned_zones`.

Format of the lists are:

`[name_of_zone,zone_id]`

## login_getwlans.py

This script builds on `login_getzone.py` to take the `cleaned_zones` list of lists and produce a list of lists called `cleaned_all_zone_wlan` that also includes the WLAN names and ids. Please note this is the WLAN name NOT the SSID.

Format of the lists are:

`[name_of_zone,zone_id,name_of_WLAN,WLAN_id]`

## login_getwlan_details.py

This script will print the JSON returned for an individual WLAN. If either of the variables `wlan_template_id` or `zone_template_id` are blank it will ask for the names of the WLAN and the zone to be inputted. The script will make an attempt to account for a spelling mistake in the WLAN name before quitting if it can not find the WLAN in the zone.

It will save the WLAN's details in a varible called `wlan_template`.
