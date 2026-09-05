# Run: python test_fetch_and_publish.py
import sys
sys.path.insert(0, "scripts")
from fetch_and_publish import missing_values

# sentinel is declared in the station's CSV header
assert missing_values(["Datum", "Tagesmittelwert", "Durchfluss in m3/s", "Fehlwerte: -777"]) == {-777.0}
# no declaration -> fall back to the portal's usual sentinel
assert missing_values(["Messstelle", "Datum", "Parameter", "Wert"]) == {-777.0}
# legit sub-zero readings (air temperature) are not sentinels
assert -2.0 not in missing_values(["Datum", "Wert", "Fehlwerte: -777"])

print("ok")
