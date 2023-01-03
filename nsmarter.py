import requests
import json
import questionary

import utils
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


with open("./config.json") as f:
    config = json.load(f)

try:
    with open("./data/stations.json") as f:
        stations = json.load(f)
except:
    stations = {}

try:
    with open("./data/presets.json") as f:
        presets = json.load(f)
except:
    presets = {}


def checkStation(id):
    arrivals = []

    resp = requests.get(
        f"{config['stationEndpointURL']}{id}",
        headers={"X-Api-Authentication": config["apikey"], "User-Agent": "nsmarter"},
    ).json()

    if resp[0]["just_coordinates"] != "1":

        for arr in resp:
            arrivals.append(
                {
                    "line": arr["line_number"],
                    "eta": arr["seconds_left"],
                    "busID": arr["vehicles"][0]["garageNo"],
                    "lastStation": arr["vehicles"][0]["station_name"],
                }
            )
    arrivals.reverse()
    return arrivals


def getArrivals(id):
    station = stations[str(id)]
    console.rule(f"Stanica {station['name']}: ")

    try:
        with console.status("Provera dolazaka je u toku!"):
            lines = checkStation(id)
    except requests.exceptions.ConnectionError:
        console.print("Proverite internet konekciju!")
        return

    if lines:
        table = Table(box=box.ROUNDED, show_lines=True)
        table.add_column("Linija", justify="center")
        table.add_column("ETA", justify="center")
        table.add_column("Trenutna stanica", justify="center")
        table.add_column("ID busa", justify="center")

        for arrival in lines:
            table.add_row(arrival['line'], utils.secondsToTimeString(arrival['eta']), arrival['lastStation'], arrival['busID'])
        console.print(table)

    else:
        console.print("Nema dolazaka!")



def searchStation(uuid):
    resp = requests.get(
        config["allStationsEndpointURL"],
        headers={
            "X-Api-Authentication": config["apikey"],
            "User-Agent": "nsmarter",
        },
    ).json()

    for station in resp["stations"]:
        if station["station_id"] == uuid:
            st = dict()

            st["name"] = station["name"]
            st["coords"] = station["coordinates"]
            st["sid"] = station["station_id"]

            return (station["id"], st)


def addStation(uuid):
    try:
        with console.status("Pretraga stanica u toku!"):
            id, station = searchStation(uuid)
    except TypeError:
        console.print("Tražena stanica nije nađena!")
        utils.emptyInput()
        return

    if stations.get(str(id)):
        console.print("Tražena stanica je već sačuvana!")
        return
    stations[str(id)] = station

    with open("./data/stations.json", "w") as f:
        json.dump(stations, f)

    console.print(f"Stanica {station['name']} je dodata!")
    


def printStations():
    console.clear()
    console.rule("NSmarter")
    stList = [stations[str(i)]["name"] for i in stations] + [
        "Unos nove stanice",
        "Izlaz",
    ]

    choice = questionary.select("Izaberite stanicu:", choices=stList).ask()

    if choice == "Unos nove stanice":
        uuid = questionary.text("Unesite ID stanice: ").ask()
        addStation(uuid)
        return

    elif choice == "Izlaz":
        console.clear()
        console.print("Hvala što ste koristili NSmarter!")
        exit()

    id = list(stations.keys())[stList.index(choice)]
    console.clear()
    getArrivals(id)
    utils.emptyInput()


if __name__ == "__main__":
    while 1 < 2:
        printStations()
