import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, MultiPolygon
from shapely import wkt
import psycopg

KML_PATH = "/Users/cullenschrock/Downloads/stonehenge-hole-1.kml"

DB_HOST = "aws-0-us-west-2.pooler.supabase.com"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres.yzpekowvyajxkeojurjg"

NS = {"kml": "http://www.opengis.net/kml/2.2"}


def get_polygon(placemark):
    coords = placemark.find(
        ".//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates",
        NS,
    )

    points = []

    for coord in coords.text.strip().split():
        lon, lat, *_ = coord.split(",")
        points.append((float(lon), float(lat)))

    return Polygon(points)


root = ET.parse(KML_PATH).getroot()

features = {}

for placemark in root.findall(".//kml:Placemark", NS):
    name = placemark.find("kml:name", NS)

    if name is None:
        continue

    name = name.text.strip()

    if name in {
        "1fairway",
        "1white-teebox",
        "1bunker1",
        "1bunker2",
        "1green",
    }:
        features[name] = get_polygon(placemark)


fairway = features["1fairway"]
tee_box = features["1white-teebox"]
bunker1 = features["1bunker1"]
bunker2 = features["1bunker2"]
green = features["1green"]

tee_point = tee_box.centroid
pin_point = green.centroid

# Combine the two bunker polygons into a single MULTIPOLYGON.
bunker_wkt = MultiPolygon([bunker1, bunker2]).wkt

print("Importing Stonehenge Golf - Hole 1")
print()
print("Tee:", tee_point.y, tee_point.x)
print("Pin:", pin_point.y, pin_point.x)
print("Fairway points:", len(fairway.exterior.coords))
print("Green points:", len(green.exterior.coords))
print("Bunkers: 2")


password = input("Enter your Supabase database password: ")

conn = psycopg.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=password,
)

with conn.cursor() as cur:
    cur.execute(
        """
        UPDATE holes
        SET
            tee_location = ST_SetSRID(ST_MakePoint(%s, %s), 4326),
            pin_location = ST_SetSRID(ST_MakePoint(%s, %s), 4326),
            green_geometry = ST_GeomFromText(%s, 4326),
            fairway_geometry = ST_GeomFromText(%s, 4326),
            bunker_geometry = ST_GeomFromText(%s, 4326)
        WHERE course_id = 6
          AND hole_number = 1
        """,
        (
            tee_point.x,
            tee_point.y,
            pin_point.x,
            pin_point.y,
            green.wkt,
            fairway.wkt,
            bunker_wkt,
        ),
    )

    print("Rows updated:", cur.rowcount)

conn.commit()
conn.close()

print("Import complete.")
