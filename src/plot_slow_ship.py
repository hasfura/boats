#!/usr/bin/python

"""
Fetches from BigQuery the ship which wastes the most time anchored, the visualizes it.
"""

import pandas as pd
from geopandas import GeoDataFrame, read_file
from geopandas.datasets import get_path
from google.cloud import bigquery
from shapely.geometry import Point
import matplotlib.pyplot as plt

AIS_CODES = {"underway": (0, "red"), "anchored": (1, "blue"), "moored": (5, "green")}
COLS_OF_INTEREST = ["lats", "lons", "statuses"]

QUERY = """
WITH
  grouped_boat_data AS (
  SELECT
    MMSI mmsi,
    ARRAY_AGG(LAT IGNORE NULLS) lats,
    ARRAY_AGG(LON IGNORE NULLS) lons,
    MAX(LAT) max_lat,
    MIN(LAT) min_lat,
    ARRAY_AGG(Status IGNORE NULLS) statuses,
    SAFE_DIVIDE(COUNTIF(Status = 1),
      COUNTIF(Status = 0)) anchored_to_underway_ratio
  FROM
    `nifty-state-339819.ais.jan_5d`
  GROUP BY
    MMSI )
SELECT
  *
FROM
  grouped_boat_data
WHERE
  ABS(max_lat - min_lat) > 10.0
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

    # Print anchored to underway ratio.
    print(f"Anchored to underway ratio: {boat_data.anchored_to_underway_ratio.iloc[0]}")

    # Explode to flatten.
    boat_data = pd.DataFrame(
        {col: boat_data[col].iloc[0].tolist() for col in COLS_OF_INTEREST}
    )

    return boat_data


def plot(boat_data):
    # Split into the different status for color coding purposes.
    status_to_data = dict(tuple(boat_data.groupby("statuses")))

    for status_name, (status_code, color) in AIS_CODES.items():
        data = status_to_data.get(status_code)
        if data is None:
            print(f"No data for status '{status_name}'. Skipping.")
            continue

        lats = data["lats"].tolist()
        lons = data["lons"].tolist()
        geometry = [Point(xy) for xy in zip(lons, lats)]
        gdf = GeoDataFrame(data, geometry=geometry)

        world = read_file(get_path("naturalearth_lowres"))
        gdf.plot(ax=world.plot(figsize=(10, 6)), marker="o", color=color, markersize=15)

    plt.show(block=True)


def main():
    boat_data = run_query()
    plot(boat_data)


if __name__ == "__main__":
    main()
