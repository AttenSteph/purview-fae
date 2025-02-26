
# purview_azure_geoip_enrich_logs.py

Parsees raw purview logs for logins, enriches with GeoIP, and makes them more readable.

The raw logs do not resolve IP addresses to location as does the Entra interactive sign-in view. While useful, that view only goes back 7 or 30 days, and the logs stored in Purview go back 180 days by default.

**For incidents that require greater than a 7 or 30 day look back geoIP is essential for determining likely malicious logins.**

This script leverages the free Maxmind GeoIP Lite database. The database is stored in the maxmind-bins/db folder but must be downloaded from Maxmind. The Maxmind supplied geoipupdate binary is used to update the DB. They are redistributed in this repo, but you may download the latest bins directly from Maxmind. https://github.com/maxmind/geoipupdate/releases

# Step 1: Get Logs

1. Login to [Purview > Audit](https://purview.microsoft.com/audit/).
2. Select your date range. If you don't know it, go ahead and set your filter for [today - 179 days ago](https://www.google.com/search?q=179+days+ago+from+today) as that is the maximum for the default log retention.
3. Enter the user names to filter on. You do not want to do this on the whole tenant. Those searches are intentionally throttled by MS and would take forever anyway if they were not.
4. Do not filter on log type. You'll want all the logs for later anyway, and the script will filter for you
5. Name the search something descriptive and run it.
6. Wait for it to complete. Open the search and click export at the top. Microsoft says it will start downloading automatically when it is complete. This is a lie. Periodically hit F5 or revisit the console sometime later and the export/download should be ready from the completed search screen.

# Step 2: Install & Run

You have two options. Option A: Download a release, extract, and run the included .exe or, option B: git clone and be able to contribute bug fixes/always be able to run the latest code.

## Option A: Download and Run Latest Release

1. Look on the side bar.
2. Download the latest 7z release file.
3. Extract it.
4. Run it.

**It will run as is as it ships with a stale copy of the MaxMind GeoIP Lite database. However, you should update that database regularly. Check the packaged README.MD for instructions on how to get a free API key and how to update.**

## Option B: Setup a Dev Environment Like a Real Woman

1. If you do not have git or python, install them.

```batchfile
winget install --silent --accept-package-agreements --accept-source-agreements git.git 
winget install --silent --accept-package-agreements --accept-source-agreements Python.Python.3.12
```

2. Clone this repo with git in some place you would like it to live

```batchfile
git clone https://github.com/AttenSteph/purview_azure_geoip_enrich_logs.git
cd purview_azure_geoip_enrich_logs
```

3. Create a python virtual environment and install python modules.
    - Note that your prompt will change to begin with (venv) after you run activate.ps1. You need to activate your virtual environment before you run the script in the future by repeating that step.

```batchfile
pip install virtualenv
virtualenv venv
.\venv\Scripts\activate.ps1
pip install -r requirements.txt
```

4. [Register for a MaxMind account.](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) Generate a license key, and then click on "Download Config". 
5. Save config as GeoIP.conf file from MaxMind and place in .\maxmind-bins\config\GeoIP.conf
6. Download up to date GeoIP database with geoipupdate tool:

```batchfile
.\maxmind-bins\geoipupdate_7.0.1_windows_amd64\geoipupdate.exe -v -f .\maxmind-bins\config\GeoIP.conf -d .\maxmind-bins\db\
```

7. Run the scriptSupply one argument, the file you need to enrich.

```batchfile
python purview_azure_geoip_enrich_logs.py some/path/to/appropriatelogfile.csv
```

**Rejoice! A new Excel file will be written and opened for your review!**
