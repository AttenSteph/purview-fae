del purview-pae_release.7z
rmdir "purview-pae_release" /S /Q
rmdir "purview-pae.onefile-build" /S /Q
rmdir "purview-pae.dist" /S /Q
rmdir "purview-pae.build" /S /Q
python -m nuitka --onefile --enable-plugin=tk-inter --windows-console-mode=force .\purview-pae.py
mkdir purview-pae_release\maxmind-bins
mkdir purview-pae_release\maxmind-local-db
copy README.MD purview-pae_release\
copy GeoIP.conf purview-pae_release\
move purview-pae.exe purview-pae_release\
xcopy /E maxmind-bins purview-pae_release\maxmind-bins\
xcopy /E maxmind-local-db purview-pae_release\maxmind-local-db\
.\build-tools\7zr.exe a .\purview-pae_release.7z .\purview-pae_release\ -mx=9 -aoa -bd