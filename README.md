# Wasserportal Data API Gateway

This repository provides an API gateway that bridges **Wasserportal Berlin** data to **Grafana** and other web applications.

## Overview

The API fetches water quality and flow data from Wasserportal Berlin monitoring stations:

- [Station 130](https://wasserportal.berlin.de/station.php?station=130) — Water quality (Wasserqualität)
- [Station 140](https://wasserportal.berlin.de/station.php?station=140) — Water quality (Wasserqualität)
- [Station 5866301](https://wasserportal.berlin.de/station.php?anzeige=d&station=5866301&thema=odf) — Flow/Discharge (Durchfluss)

It then processes and publishes the data as JSON through **GitHub Pages**, making it easily consumable by visualization tools like Grafana or websites.

## Data Update Schedule

Data is automatically updated **once per day** via a **GitHub Actions** workflow.  
This ensures that the JSON output always reflects the latest available measurements.

## Repository

- GitHub Repository: [idonov8/wasserportal-data](https://github.com/idonov8/wasserportal-data)

## Output

The generated JSON files are publicly available through GitHub Pages at:

- https://idonov.com/wasserportal-data/stations/130.json
- https://idonov.com/wasserportal-data/stations/140.json
- https://idonov.com/wasserportal-data/stations/5866301.json

## Grafana Dashboards

Two Grafana dashboard definitions are included:

- `grafana-dashboard.json` — Water quality dashboard for stations 130 and 140
- `grafana-flow-5866301.json` — Flow/discharge dashboard for station 5866301
