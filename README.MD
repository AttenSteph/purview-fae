# purview_azure_geoip_enrich_logs.py
Parsees raw purview logs, enriches with GeoIP, and makes them more readable.

The raw logs do not resolve IP addresses to location as does the Entra interactive sign-in view. While useful, that view only goes back 7 or 30 days, and the logs stored in Purview go back 180 days by default.

**For incidents that require greater than a 7 or 30 day look back geoIP is essential for determining likely malicious logins.**

This script leverages the free Maxmind GeoIP Lite database. The database is stored in the maxmind-bins/db folder but must be downloaded from Maxmind. The Maxmind supplied geoipupdate binary is used to update the DB. They are redistributed in this repo, but you may download the latest bins directly from Maxmind. https://github.com/maxmind/geoipupdate/releases


# 1) Get Logs

Login to [Purview > Audit](https://purview.microsoft.com/audit/).
- Select your date range. If you don't know it, go ahead and set your filter for [today - 179 days ago](https://www.google.com/search?q=179+days+ago+from+today) as that is the maximum for the default log retention.
- Enter the user names to filter on. You do not want to do this on the whole tenant. Those searches are intentionally throttled by MS and would take forever anyway if they were not.
- Do not filter on log type. You'll want all the logs for later anyway, and the script will filter for you
- Name the search something descriptive and run it.
- Wait for it to complete. Open the search and click export at the top. Microsoft says it will start downloading automatically when it is complete. This is a lie. Periodically hit F5 or revisit the console sometime later and the export/download should be ready from the completed search screen.


# 2) Install & Run

You have two options. Option A: Download a release, extract, and run the included .exe or, option B: git clone and be able to contribute bug fixes/always be able to run the latest code.

## Option A: Download and Run Latest Release

- Look on the side bar.
- Download the latest 7z release file.
- Extract it.
- Run it.

It will run as is as it ships with a stale copy of the MaxMind GeoIP Lite database, but you really want to update that database, so I suggest you check the packaged README.MD and sign up for a MaxMind account, and get an API key.

## Option B: Setup a Dev Environment Like a Real Woman

- If you do not have git or python, install them.
```
winget install --silent --accept-package-agreements --accept-source-agreements git.git 
winget install --silent --accept-package-agreements --accept-source-agreements Python.Python.3.12
```
- Clone this repo with git in some place you would like it to live
```
git clone https://github.com/AttenSteph/purview_azure_geoip_enrich_logs.git
cd purview_azure_geoip_enrich_logs
```
- Create a python virtual environment and install python modules.
 - Note that your prompt will change to begin with (venv) after you run activate.ps1. You need to activate your virtual environment before you run the script in the future by repeating that step.
```
pip install virtualenv
virtualenv venv
.\venv\Scripts\activate.ps1
pip install -r requirements.txt
```
- [Register for a MaxMind account.](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) Generate a license key, and then click on "Download Config". 
- Save config as GeoIP.conf file from MaxMind and place in .\maxmind-bins\config\GeoIP.conf
- Download up to date GeoIP database with geoipupdate tool:
```
.\maxmind-bins\geoipupdate_7.0.1_windows_amd64\geoipupdate.exe -f .\maxmind-bins\config\GeoIP.conf -d .\maxmind-bins\db\
```
- Run the scriptSupply one argument, the file you need to enrich.
```
python purview_azure_geoip_enrich_logs.py some/path/to/appropriatelogfile.csv
```
A new Excel file will be written and opened for your review.
