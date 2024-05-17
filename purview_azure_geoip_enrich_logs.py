import argparse
import json
import geoip2.database
import pandas as pd


def geoip_lookup(json_data):
    # Parse the JSON data
    data = json.loads(json_data)

    # Extract the ClientIP value
    client_ip = data.get("ClientIP")

    if client_ip:
        # Perform GeoIP lookup
        reader = geoip2.database.Reader("maxmind-bins/db/GeoLite2-City.mmdb")
        try:
            response = reader.city(client_ip)
            city = response.city.name
            country = response.country.name
            fulllocation = city + ", " + country
            return fulllocation
        except geoip2.errors.AddressNotFoundError:
            return "NOT_FOUND"
        finally:
            reader.close()
    else:
        print("NOT_FOUND")


def enrich_df(dataframe):
    for index, row in dataframe.iterrows():
        location = geoip_lookup(row["AuditData"])
        df.at[index, "GeoIPLocation"] = location


# argument handling
parser = argparse.ArgumentParser()
parser.add_argument('filename', help="Path to the csv file to enrich.")
args = parser.parse_args()

# read csv file in
with open(args.filename, 'r') as mscsvfile:
    df = pd.read_csv(mscsvfile)

# insert an empty column for our geoIP results
df['GeoIPLocation'] = None

# enrich data with geoip info
enrich_df(df)

# write out enriched file
newfile = args.filename[:-4] + "_geoip_enriched.csv"
df.to_csv(newfile, index=False)
print("GeoIP enriched log data written to " + newfile)
