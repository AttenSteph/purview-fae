# purview_azure_geoip_enrich_logs.py
Quick script to parse raw purview logs when exporting login/logout info by selecting all "entra" records in the console. The raw logs do not resolve IP addresses to location as does the Entra interactive sign-in view. While useful, that view only goes back 7 days, and the logs stored in Purview go back 180 days by default.

For incidents that require greater than a 7 day look back geoIP is essential for determining likely malicious logins.

This script leverages the free Maxmind GeoIP Lite database. The database is stored in the maxmind-bins/db folder but must be downloaded from Maxmind. The geoipupdate tools is leveraged to do this and a copy is included in this repo. You may also download these bins directly from Maxmind. https://github.com/maxmind/geoipupdate/releases

To create/update the database run the maxmind-bins/geoipupdate_7.0.1_windows_amd64/update.bat file and it will use the config in maxmind-bins/config/GeoIP.conf. You can download this config directly from MaxMind after setting up a free account with them. https://dev.maxmind.com/geoip/geolite2-free-geolocation-data, generating a license key, and then clicking on "Download Config". Place that file in the appropriate location and run the aformentioned batch file.

**INSTALL & USAGE**

**First - Get Logs:**

log in to Purview > Audit.
- Select your date range. If you don't know it, go ahead and set your filter for today - 180 days as that is the maximum default log retention.
- Enter the user names to filter on. You do not want to do this on the whole tenant. Those searches are intentionally throttled by MS and would take forever anyway if they were not.
- Do not filter on log type. You'll want all the logs for later anyway.
- Name the search something descriptive and run it.
- Wait for it to complete. Open the search and click export at the top. Microsoft says it will start downloading automatically when it is complete. This is a lie. Periodically hit F5 or revisit the console sometime later and the export/download should be ready from the completed search screen.
- You will have a .csv file. Go ahead and filter this by RecordType = "15", and Operation = "UserLoggedIn". These are your logins. You can do this in excel, or with grep if you are feeling fancy. Make these a new .csv

**Second - Install & Run Script:**
- Clone this repo with git in some place you would like it to live
```
PS > git clone https://github.com/AttenSteph/purview_azure_geoip_enrich_logs.git
PS > cd purview_azure_geoip_enrich_logs
```
- Download a GeoIP.conf file from MaxMind and place in .\maxmind-bins\config\GeoIP.conf
- Download up to date GeoIP database:
```
PS > .\maxmind-bins\geoipupdate_7.0.1_windows_amd64\update.bat
```
- Create a python virtual environment and install modules. Something like:
```
PS> virtualenv --no-site-packages --distribute .env
PS> pip install -r requirements.txt
```

- Start the python virtual environment. Supply one argument, the file you need to enrich.

```
PS C:\purview_azure_geoip_enrich_logs> .\venv\Scripts\activate.ps1
(venv) PS C:\purview_azure_geoip_enrich_logs> python purview_azure_geoip_enrich_logs.py some/path/to/appropriatelogfile.csv
GeoIP enriched log data written to some/path/to/appropriatelogfile_geoip_enriched.csv
```

Check your new file, that's it.