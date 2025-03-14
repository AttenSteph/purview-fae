import argparse
import json
import os
import sys
import geoip2.database
import geoip2.errors
import pandas as pd
from rdns_reaper import RdnsReaper
from colorama import init, Fore
from easygui import *

# set auto reset for colorama print messages
init(autoreset=True)

def de_dupe_ips(dataframe):
    """get list of unique ips from dataframe and deduplicate"""
    data = []
    unique_ips = []
    for index, row in dataframe.iterrows():
        jsondata = json.loads((row["AuditData"]))
        data.append(jsondata.get("ClientIP"))
        unique_ips = list(set(data))
    return unique_ips


def ip2dns(ipaddresses):
    """reverse IP lookup using dnsreaper"""
    rdr = RdnsReaper(limit_to_rfc1918=False, concurrent=200, unresolvable=r"HOSTNOTFOUND")
    rdr.add_ip_list(ipaddresses)
    rdr.resolve_all()
    return rdr.get_dict()


def geoip_lookup(json_data):
    """perform geoip lookup with offline maxmind database"""
    try:
        data = json.loads(json_data)
    except Exception as ejson:
        print(Fore.YELLOW + "[*] " + Fore.RESET + "Failed to parse JSON in geoip_lookup")
        print(Fore.YELLOW + "[*] " + Fore.RESET + "Exception: %s" % str(ejson))

    # Extract the ClientIP value
    try:
        client_ip = data.get("ClientIP")
    except Exception as eclientip:
        print(Fore.YELLOW + "[*] " + Fore.RESET + "Failed to extract ClientIP value")
        print(Fore.YELLOW + "[*] " + Fore.RESET + "Exception: %s" % str(eclientip))

    # TODO refactor
    if client_ip:
        # Perform GeoIP lookup
        reader = geoip2.database.Reader("maxmind-local-db/GeoLite2-City.mmdb")
        try:
            response = reader.city(client_ip)
            city = response.city.name
            # state = response.subdivisions
            country = response.country.name
            # fulllocation = str(city) + ", " + str(state) + "  " + str(country)
            fulllocation = str(city) + ", " + str(country)
            # print(fulllocation, client_ip)
            return fulllocation, client_ip
        except geoip2.errors.AddressNotFoundError as egeoip:
            print(Fore.YELLOW + "[*] " + Fore.RESET + "Exception with geoip lookup for " + client_ip)
            print(Fore.YELLOW + "[*] " + Fore.RESET + "Exception: %s" % str(egeoip))
            return "NOT_FOUND", client_ip
        finally:
            reader.close()
    else:
        return "NOT_FOUND", "NOT_FOUND"


def enrich_df(dataframe, ip2dnslookkupdict):
    """enrich dataframe with reverse dns and geoip information"""
    for index, row in dataframe.iterrows():
        data = geoip_lookup(row["AuditData"])
        df.at[index, "GeoIPLocation"] = str(data[0])
        try:
            df.at[index, "HostName"] = ip2dnslookkupdict[str(data[1])]
        except KeyError as keye:
            print(Fore.YELLOW + "[*] " + Fore.RESET + "IP2DNS dictionary key lookup failure.")
            print(Fore.YELLOW + "[*] " + Fore.RESET + "Exception: %s" % str(keye))
        df.at[index, "IPAddress"] = str(data[1])
        df.at[index, "MultiGeoIPLink"] = "https://www.iplocation.net/ip-lookup" #TODO temporary until broader api support


# basic argument handling
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', help="CSV file input.", required=False)
args = parser.parse_args()

if not args.filename:
    # Open file GUI
    print("Select a Purview CSV file export in the file open dialogue.")
    title = "Open Purview Logs"
    msg = "Click OK and select your Purview logs to filter."
    filename = fileopenbox(msg,title)
else:
    filename = args.filename

# open the file; fixed file encoding parsing issues by forcing utf8 and backslash escaping
file_encoding = 'utf8'  # set file_encoding to the file encoding (utf8, latin1, etc.)
input_fd = open(filename, encoding=file_encoding, errors='backslashreplace')
df = pd.read_csv(input_fd)

# insert an empty column for our geoIP results, and IP address
df['GeoIPLocation'] = None
df['HostName'] = None
df['IPAddress'] = None
df['MultiGeoIPLink'] = None

# reduce data frame to only colum "RecordType", value = "15"
df = df.loc[df['RecordType'] == 15]

# do DNS lookups once
print(Fore.CYAN + "[*] " + Fore.RESET + "Performing DNS reverse lookups...")
ips2resolve = de_dupe_ips(df)
ips2resolve = [i for i in ips2resolve if i] # remove empty strings with list comprehension
ip2dnsdictionary = ip2dns(ips2resolve)
print(Fore.GREEN + "[*] " + Fore.RESET + "Completed DNS reverse lookups.")

# enrich data with geoip info
print(Fore.CYAN + "[*] " + Fore.RESET + "Enriching data...")
enrich_df(df, ip2dnsdictionary)
print(Fore.GREEN + "[*] " + Fore.RESET + "Data enriched.")

# write out enriched file
print(Fore.CYAN + "[*] " + Fore.RESET + "Writing Excel file...")
try:
    newfile = filename[:-4] + "_geoip_enriched.xlsx"
    df.to_excel(newfile, index=False)
    print(Fore.GREEN + "[*] " + Fore.RESET + "GeoIP enriched log data written to " + newfile)
except Exception as e:
    print(Fore.RED + "[*] " + Fore.RESET + "Can't write file. Is a file in the same location already open in Excel?")
    print ("Exception: %s" % str(e))
    sys.exit(1)

# open it in default app
try:
    print(Fore.CYAN + "[*] " + Fore.RESET + "Opening Excel file " + newfile)
    os.startfile(newfile, 'open')
except Exception as e:
    print(Fore.RED + "[*] " + Fore.RESET + "Can't open file. Something went very wrong.")
    print ("Exception: %s" % str(e))
    sys.exit(1)

# pause to not close the window in case it was just double-clicked
os.system('pause')
