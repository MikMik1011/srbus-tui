from . import data, utils
import requests

allStations = None


def checkStation(id):
    arrivals = []

    resp = requests.get(
        f"{data.config['stationEndpointURL']}{id}",
        headers={
            "X-Api-Authentication": data.config["apikey"],
            "User-Agent": "bg++",
        },
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


def searchStationByUUID(uuid):
    global allStations
    if not allStations:
        allStations = requests.get(
            data.config["allStationsEndpointURL"],
            headers={
                "X-Api-Authentication": data.config["apikey"],
                "User-Agent": "bg++",
            },
        ).json()

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
        allStations = requests.get(
            data.config["allStationsEndpointURL"],
            headers={
                "X-Api-Authentication": data.config["apikey"],
                "User-Agent": "bg++",
            },
        ).json()

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
