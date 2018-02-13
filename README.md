# General

Generic script for importing excel data into iso 19115 and 191110 

## xls2iso install

Scripts use python3 and it better to have pip3 installed for package installation (management)

Mac install: (http://itsevans.com/install-pip-osx/)

Linux install: `apt install python3-pip`

Windows: (https://stackoverflow.com/questions/24285508/how-to-use-pip-with-python-3-4-on-windows)


On the folder or each script the necessary python packages are in the `requirements.txt` file to install them:
```
pip3 -r requirements.txt
```

## xls2iso run

```
python3 xls2iso19115.py [-h] [--schema|--no-schema] [--excelsheet ./md.xslx]  [--outdir ./output]
```

Make sure --outdir is available and has write privileges