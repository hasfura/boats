#!/bin/bash

# This script does a few things:
# 1. Downloads AIS zip files from `https://marinecadastre.gov/ais/`.
# 2. Unzips the AIS files (turns into a single .csv).
# 3. Concatenates the csv them into month-long files (~15GB a piece).
# 4. Uploads to GCS, for further processing with BigQuery.
#
# Run with default args: ./tools/install_ais_data.sh
# RUn with custom args: ./tools/install_ais_data.sh /tmp/harris_smells 2021 2 4
#
# I didn't take the time to do parameter validation so don't specify dumb stuff.

set -e

# User specified arguments.
ROOT_DIR=${1:-/tmp/ais}
YEAR=${2:-2020}
START_MONTH=${3:-1}
END_MONTH=${4:-12}

# Constants.
DOWNLOAD_URL=https://coast.noaa.gov/htdata/CMSP/AISDataHandler/${YEAR}
GCS_PATH=gs://hasfura/boats/ais/

mkdir -p ${ROOT_DIR}

for month in `seq -f "%02g" ${START_MONTH} ${END_MONTH}`; do
  touch ${ROOT_DIR}/${YEAR}_${month}.csv

  for day in `seq -f "%02g" 1 31`; do
    url=${DOWNLOAD_URL}/AIS_${YEAR}_${month}_${day}.zip
    echo "Downloading ${url}."

    # 1. Downloads AIS zip files from `https://marinecadastre.gov/ais/`.
    if curl --silent --fail ${url} -o ${ROOT_DIR}/${YEAR}_${month}_${day}.zip; then
      # 2. Unzips the AIS files (turns into a single .csv).
      unzip -q ${ROOT_DIR}/${YEAR}_${month}_${day}.zip -d ${ROOT_DIR}/${YEAR}_${month}_${day}

      # 3. Concatenates the csv them into month-long files (~15GB a piece).
      # Throws out first line (headers).
      sed '1d' ${ROOT_DIR}/${YEAR}_${month}_${day}/AIS_${YEAR}_${month}_${day}.csv >> ${ROOT_DIR}/${YEAR}_${month}.csv

      # 4. Clean up.
      rm -r ${ROOT_DIR}/${YEAR}_${month}_${day}/
      rm ${ROOT_DIR}/${YEAR}_${month}_${day}.zip
    fi
  done

  # 4. Uploads to GCS, for further processing with BigQuery.
  gsutil cp ${ROOT_DIR}/${YEAR}_${month}.csv ${GCS_PATH}
  rm ${ROOT_DIR}/${YEAR}_${month}.csv
done

# Read what is at GCS path
gsutil ls ${GCS_PATH}
