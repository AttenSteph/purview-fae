import argparse
import json
import os
from tkinter.constants import FALSE

import geoip2.database
import geoip2.errors
import pandas as pd
import socket

def de_dupe_ips(dataframe):
    data = []
    unique_ips = []
    for index, row in dataframe.iterrows():
        jsondata = json.loads((row["AuditData"]))
        data.append(jsondata.get("ClientIP"))
        unique_ips = list(set(data))
    return unique_ips


# noinspection PyBroadException
def ip2dns(ipaddresses):
    ip2dnsdict = {}
    for ip in ipaddresses:
        try:
            hostname = socket.gethostbyaddr(ip)
            ip2dnsdict[ip] = hostname[0]
        except:
            hostname = "HOSTNOTFOUND"
            ip2dnsdict[ip] = hostname
    return ip2dnsdict


def geoip_lookup(json_data):
    # TODO Add argument and parsing for marking known registered devices as low risk. Sample JSON:
    # "DeviceProperties": [
    #     {"Name": "Id", "Value": "<guid>"},
    #     {"Name": "DisplayName", "Value": "<computername>"},
    #     {"Name": "OS", "Value": "Windows"},
    #     {"Name": "BrowserType", "Value": "Other"},
    #     {"Name": "TrustType", "Value": "1"},
    #     {"Name": "SessionId", "Value": "<guid>"}
    # ],
    # Parse the JSON data
    data = json.loads(json_data)

    # Extract the ClientIP value
    client_ip = data.get("ClientIP")

    # TODO see above comment; Extract DeviceID
    # device_id = data.get("Id")

    if client_ip:
        # Perform GeoIP lookup
        reader = geoip2.database.Reader("maxmind-bins/db/GeoLite2-City.mmdb")
        try:
            response = reader.city(client_ip)
            city = response.city.name
            # state = response.subdivisions
            country = response.country.name
            # fulllocation = str(city) + ", " + str(state) + "  " + str(country)
            fulllocation = str(city) + ", " + str(country)
            # print(fulllocation, client_ip)
            return fulllocation, client_ip
        except geoip2.errors.AddressNotFoundError:
            # print(client_ip)
            return "NOT_FOUND", client_ip
        finally:
            reader.close()
    else:
        print("NOT_FOUND")
        return "NOT_FOUND", "NOT_FOUND"


def enrich_df(dataframe, ip2dnslookkupdict):
    for index, row in dataframe.iterrows():
        data = geoip_lookup(row["AuditData"])
        df.at[index, "GeoIPLocation"] = str(data[0])
        df.at[index, "HostName"] = ip2dnslookkupdict[str(data[1])]
        df.at[index, "IPAddress"] = str(data[1])
        df.at[index, "MultiGeoIPLink"] = "https://www.iplocation.net/ip-lookup" #TODO temporary until broader api support


# argument handling
parser = argparse.ArgumentParser()
parser.add_argument('filename', help="Path to the csv file to enrich.")
args = parser.parse_args()

# open the file; fixed file encoding parsing issues by forcing utf8 and back slash escaping
file_encoding = 'utf8'  # set file_encoding to the file encoding (utf8, latin1, etc.)
input_fd = open(args.filename, encoding=file_encoding, errors='backslashreplace')
df = pd.read_csv(input_fd)

# insert an empty column for our geoIP results, and IP address
df['GeoIPLocation'] = None
df['HostName'] = None
df['IPAddress'] = None
df['MultiGeoIPLink'] = None

# reduce data frame to only colum "RecordType", value = "15"
df = df.loc[df['RecordType'] == 15]

# do DNS lookups once
ips2resolve = de_dupe_ips(df)
ip2dnsdictionary = ip2dns(ips2resolve)

# enrich data with geoip info
enrich_df(df, ip2dnsdictionary)

# write out enriched file
newfile = args.filename[:-4] + "_geoip_enriched.xlsx"
df.to_excel(newfile, index=False)
print("GeoIP enriched log data written to " + newfile)

# open it in default app
print("Opening file...")
os.startfile(newfile, 'open')
