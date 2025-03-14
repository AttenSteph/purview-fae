import ipinfo
import pprint

access_token = '' # get from ipinfo.io
handler = ipinfo.getHandler(access_token)
ip_address = '1.1.1.1'
details = handler.getDetails(ip_address)
# pprint.pprint(details.all)
print(details.country_name, details.region, details.city)
print(details.ip, details.hostname)
print(details.org)
