# purview_azure_geoip_enrich_logs.py
Quick script to parse raw purview logs when exporting login/logout info by selecting all "entra" records in the console. The raw logs do not resolve IP addresses to location as does the Entra interactive sign-in view. While useful, that view only goes back 7 days, and the logs stored in Purview go back 180 days by default.

For incidents that require greater than a 7 day look back geoIP is essential.

This script leverages the free Maxmind GeoIP Lite database. The database is stored in the maxmind-bins/db folder but must be downloaded from Maxmind. The geoipupdate tools is leveraged to do this and a copy is included in this repo. You may also download these bins directly from Maxmind. https://github.com/maxmind/geoipupdate/releases

To create/update the database run the maxmind-bins/geoipupdate_7.0.1_windows_amd64/update.bat file and it will use the config in maxmind-bins/config/GeoIP.conf. You can download this config directly from MaxMind after setting up a free account with them. https://dev.maxmind.com/geoip/geolite2-free-geolocation-data, generating a license key, and then clicking on "Download Config". Place that file in the appropriate location and run the aformentioned batch file.

Usage is simple. Start the python virtual environment. Supply one argument, the file you need to enrich.

```
PS C:\purview_azure_geoip_enrich_logs> .\venv\Scripts\activate.ps1
(venv) PS C:\purview_azure_geoip_enrich_logs> python purview_azure_geoip_enrich_logs.py some/path/to/appropriatelogfile.csv
GeoIP enriched log data written to some/path/to/appropriatelogfile_geoip_enriched.csv
```

Check your new file, that's it.