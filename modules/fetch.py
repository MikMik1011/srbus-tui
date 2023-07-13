from . import data, utils
import requests

allStations = None

if not data.config["city"] in data.getCities():
    baseUrl = None
    headers = None
else:
    baseUrl = data.apikeys[data.config["city"]]["url"]
    headers = {
        "X-Api-Authentication": data.apikeys[data.config["city"]]["key"],
        "User-Agent": "srbus",
    }


def updateCity():
    global headers, baseUrl, allStations

    allStations = None

    baseUrl = data.apikeys[data.config["city"]]["url"]
    headers = {
        "X-Api-Authentication": data.apikeys[data.config["city"]]["key"],
        "User-Agent": "srbus",
    }


def checkStation(id):
    arrivals = []

    global headers

    url = baseUrl + data.config["stationEndpointRoute"] + id

    resp = requests.get(
        url,
        headers=headers,
    ).json()

    if resp[0]["just_coordinates"] != "1":
        for arr in resp:
            diff = utils.stationDifference(
                arr["all_stations"], id, arr["vehicles"][0]["station_number"]
            )
            if diff < 0:
                continue

            arrivals.append(
                {
                    "line": arr["line_number"],
                    "eta": arr["seconds_left"],
                    "busID": arr["vehicles"][0]["garageNo"],
                    "lastStation": arr["vehicles"][0]["station_name"],
                    "stationDiff": str(diff),
                }
            )
    arrivals.reverse()
    return arrivals


def fetchAllStations():
    global allStations, headers

    if not allStations:
        url = baseUrl + data.config["allStationsEndpointRoute"]
        allStations = requests.get(
            url,
            headers=headers,
        ).json()

    return allStations


def searchStationByUUID(uuid):
    global allStations
    if not allStations:
        allStations = fetchAllStations()

    uuid = uuid.lower()

    for station in allStations["stations"]:
        if station["station_id"].lower() == uuid:
            st = dict()

            st["name"] = station["name"]
            st["coords"] = station["coordinates"]
            st["sid"] = station["station_id"]

            return (station["id"], st)


def searchStationByName(name):
    global allStations

    if not allStations:
        allStations = fetchAllStations()

    name = name.lower()

    eligibleStations = {}

    for station in allStations["stations"]:
        if name in utils.cirULat(station["name"].lower()):
            st = dict()
            st["name"] = station["name"]
            st["coords"] = station["coordinates"]
            st["sid"] = station["station_id"]

            eligibleStations[str(station["id"])] = st

    return eligibleStations
