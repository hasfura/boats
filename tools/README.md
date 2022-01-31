# Overveiw
Set of tools used for boat work. Each script will have a small description below.

### install_ais_data.sh
This tool is a bash script to download the full 2020 year of AIS data, collect into files the size of months, then install in GCS folder at `gs://hasfura/boats/ais`.

To execute:
```bash
# Run with default configuration, downloading full year of 2020.
./tools/install_ais_data.sh <YOUR_LOCAL_DIR> <YEAR> <START_MONTH> <END_MONTH>

# Run with some command line arguments.
./tools/install_ais_data.sh <YOUR_LOCAL_DIR> <YEAR> <START_MONTH> <END_MONTH>
```

You should see some logs like the following:
```bash
~/dev/boats/tools $ ./tools/install_ais_data.sh

Downloading https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2020/AIS_2020_01_01.zip.
Downloading https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2020/AIS_2020_01_02.zip.
Downloading https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2020/AIS_2020_01_03.zip.
Downloading https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2020/AIS_2020_01_04.zip.
Downloading https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2020/AIS_2020_01_05.zip.
Downloading https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2020/AIS_2020_01_06.zip.
Downloading https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2020/AIS_2020_01_07.zip.
...
```

I didn't take the time to implement command line argument validation, so be sure to input correctly.
e.g., `start_month < end_month`, `1 <= *_month <=12`, etc.
