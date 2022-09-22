import json
import re
from urllib import request

URL = "https://www.pycon.jp/support/bootcamp.html"
with request.urlopen(URL) as f:
    html = f.read().decode("utf-8")
pattern = re.compile(r"pyconjp.*/event/(\d+)/(?!.*中止)")
ids = ",".join(pattern.findall(html))

connpass_api = "https://connpass.com/api/v1/event/"
url = f"{connpass_api}?event_id={ids}&count=100"
with request.urlopen(url) as f:
    data = json.load(f)

features = [{
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [float(e["lon"]), float(e["lat"])],
    },
    "properties": {"name": e["title"]},
} for e in data["events"]]
geo = {"type": "FeatureCollection", "features": features}

with open("pycamp.geojson", "w") as f:
    json.dump(geo, f, indent=2, ensure_ascii=False)
print("Number of events:", len(features))  # -> 45

print("It's your turn.")
