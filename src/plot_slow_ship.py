#!/usr/bin/python

"""
Fetches from BigQuery the ship which wastes the most time anchored, the visualizes it.
"""

QUERY = """
SELECT * FROM `nifty-state-339819.ais.test` limit 10
"""

import pandas as pd
from geopandas import GeoDataFrame, read_file
from geopandas.datasets import get_path
from google.cloud import bigquery
from shapely.geometry import Point
import matplotlib.pyplot as plt

AIS_CODES = {0: "underway", 1: "anchored", 5: "moored"}

QUERY = """
SELECT
  MMSI mmsi,
  ARRAY_AGG(LAT) lats,
  ARRAY_AGG(LON) lons,
  ARRAY_AGG(Status) statuses,
  SAFE_DIVIDE(COUNTIF(Status = 1),
    COUNTIF(Status = 0)) anchored_to_underway_ratio
FROM
  `nifty-state-339819.ais.test`
GROUP BY
  MMSI
ORDER BY
  anchored_to_underway_ratio DESC
LIMIT
  1
"""


def run_query():
    bq_client = bigquery.Client()

    # Download query results.
    boat_data = (
        bq_client.query(QUERY)
        .result()
        .to_dataframe(
            create_bqstorage_client=True,
        )
    )

    # Explode to flatten.
    boat_data = (
        boat_data.explode("lats")
        .explode("lons")
        .explode("statuses")
        .reset_index(drop=True)
    )

    return boat_data


def plot(boat_data):
    lats = boat_data["lats"].tolist()
    lons = boat_data["lons"].tolist()
    geometry = [Point(xy) for xy in zip(lons, lats)]
    gdf = GeoDataFrame(boat_data, geometry=geometry)

    world = read_file(get_path("naturalearth_lowres"))
    gdf.plot(ax=world.plot(figsize=(10, 6)), marker="o", color="red", markersize=15)
    plt.show(block=True)


def main():
    boat_data = run_query()
    plot(boat_data)


if __name__ == "__main__":
    main()
