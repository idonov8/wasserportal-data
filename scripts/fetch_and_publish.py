# scripts/fetch_and_publish.py
# Python 3.9+
import requests
import csv
import os
from datetime import datetime
from dateutil import parser as dateparser

OUT_DIR = "public/stations"
os.makedirs(OUT_DIR, exist_ok=True)

STATIONS = [
    {"id": "140", "filename": "140.json"},
    {"id": "130", "filename": "130.json"},
]

BASE_URL = "https://wasserportal.berlin.de/station.php?anzeige=d&station={station}&thema=opq&nstoffid=448&nstoffid2=0"

def detect_delimiter(first_line: str):
    # prefer semicolon if present (common in German CSVs)
    if ";" in first_line and "," not in first_line:
        return ";"
    if ";" in first_line and "," in first_line:
        # ambiguous, choose semicolon
        return ";"
    return ","

def find_keys(header):
    # Try to locate date and value keys (case-insensitive)
    header_lower = [h.lower() for h in header]
    date_key = None
    value_key = None
    for h, hl in zip(header, header_lower):
        if any(x in hl for x in ("datum", "date", "zeit")) and date_key is None:
            date_key = h
        if any(x in hl for x in ("wert", "value", "messwert")) and value_key is None:
            value_key = h
    # fallback to first two columns
    if date_key is None and len(header) >= 1:
        date_key = header[0]
    if value_key is None and len(header) >= 2:
        value_key = header[1]
    return date_key, value_key

def parse_number(s: str):
    if s is None:
        return None
    s = s.strip()
    if s == "" or s in ("-", "n.a.", "NaN"):
        return None
    # replace German decimal comma
    s = s.replace(".", "") if s.count(",") > 0 and s.count(".") == 0 and "," in s and s.replace(",", "").isdigit() else s
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def parse_date(s: str):
    if not s:
        return None
    s = s.strip()
    try:
        # handle common German format dd.mm.YYYY HH:MM or dd.mm.YYYY
        # dateutil parser handles most cases
        dt = dateparser.parse(s, dayfirst=True)
        return dt
    except Exception:
        return None

def fetch_station(station_id: str):
    url = BASE_URL.format(station=station_id)
    # prepare form payload with start date and today
    payload = {
        "sreihe": "ew",
        "smode": "c",
        "sdatum": "02.01.1975",
        "senddatum": datetime.now().strftime("%d.%m.%Y"),
        "exportthema": "pq",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://wasserportal.berlin.de",
        "Referer": "https://wasserportal.berlin.de/",
        "User-Agent": "github-actions-fetcher/1.0",
    }

    resp = requests.post(url, data=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    text = resp.text

    # detect delimiter using the first non-empty line
    lines = [ln for ln in text.splitlines() if ln.strip() != ""]
    if not lines:
        return []
    delim = detect_delimiter(lines[0])
    reader = csv.DictReader(lines, delimiter=delim)
    header = reader.fieldnames or []
    date_key, value_key = find_keys(header)

    out = []
    for row in reader:
        raw_date = row.get(date_key, "").strip() if date_key else ""
        raw_value = row.get(value_key, "").strip() if value_key else ""
        dt = parse_date(raw_date)
        if dt is None:
            # skip rows without a valid date
            continue
        val = parse_number(raw_value)
        # some entries may include extra info; still include nulls
        out.append({
            "time": dt.isoformat(),
            "value": val,
            "raw_value": raw_value,
            "raw_row": row
        })
    # sort by time ascending
    out.sort(key=lambda r: r["time"])
    return out

def main():
    index = {"generated": datetime.utcnow().isoformat() + "Z", "stations": []}
    for s in STATIONS:
        print(f"Fetching station {s['id']}...")
        try:
            data = fetch_station(s["id"])
        except Exception as e:
            print(f"Error fetching station {s['id']}: {e}")
            data = []
        out_obj = {
            "station": s["id"],
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "count": len(data),
            "data": data,
        }
        out_path = os.path.join(OUT_DIR, s["filename"])
        with open(out_path, "w", encoding="utf-8") as f:
            import json
            json.dump(out_obj, f, ensure_ascii=False, indent=2)
        index["stations"].append({
            "id": s["id"],
            "url": f"./{s['filename']}",
            "count": len(data)
        })
        print(f"Wrote {out_path} ({len(data)} rows)")

    # write index file
    index_path = os.path.join("public", "stations.json")
    with open(index_path, "w", encoding="utf-8") as f:
        import json
        json.dump(index, f, ensure_ascii=False, indent=2)
    print("Wrote stations index:", index_path)


if __name__ == "__main__":
    main()
