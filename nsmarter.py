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
                    "stationDiff": utils.stationDifference(
                        arr["all_stations"], id, arr["vehicles"][0]["station_number"]
                    ),
                }
            )
    arrivals.reverse()
    return arrivals


def getArrivals(id):
    station = stations[str(id)]
    console.rule(f"Stanica {station['name']} ({station['sid']}):")

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
        table.add_column("Br. stanica", justify="center")
        table.add_column("Trenutna stanica", justify="center")
        table.add_column("ID busa", justify="center")

        for arrival in lines:
            table.add_row(
                arrival["line"],
                utils.secondsToTimeString(arrival["eta"]),
                arrival["stationDiff"],
                arrival["lastStation"],
                arrival["busID"],
            )
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
        console.print("[bold red]Tražena stanica nije nađena!")
        utils.emptyInput()
        return

    if stations.get(str(id)):
        console.print("[bold red]Tražena stanica je već sačuvana!")
        utils.emptyInput()
        return
    stations[str(id)] = station

    with open("./data/stations.json", "w") as f:
        json.dump(stations, f)

    console.print(f"Stanica {station['name']} [green] je sačuvana!")
    utils.emptyInput()


def printStations():
    console.clear()
    console.rule("Stanice")
    stList = [
        f"{stations[str(i)]['name']} ({stations[str(i)]['sid']})" for i in stations
    ] + [
        "Unos nove stanice",
        "Izlaz",
    ]

    choice = questionary.select("Izaberite stanicu:", choices=stList).ask()

    if choice == "Unos nove stanice":
        uuid = questionary.text("Unesite ID stanice: ").ask()
        addStation(uuid)
        return

    elif choice == "Izlaz":
        return

    id = list(stations.keys())[stList.index(choice)]
    console.clear()
    getArrivals(id)

    utils.emptyInput()


def printPresets():
    console.clear()
    console.rule("Preseti")

    prList = [i for i in presets.keys()] + ["Napravi novi preset", "Izlaz"]

    choice = questionary.select("Izaberite preset:", choices=prList).ask()

    if choice == "Napravi novi preset":
        name = questionary.text("Unesite ime preseta: ").ask()
        stList = [
            f"{stations[str(i)]['name']} ({stations[str(i)]['sid']})" for i in stations
        ]

        stNames = questionary.checkbox("Izaberite stanice:", choices=stList).ask()
        stIDs = [list(stations.keys())[stList.index(i)] for i in stNames]
        presets[name] = stIDs

        with open("./data/presets.json", "w") as f:
            json.dump(presets, f)

        console.print(f"Preset {name} [green]je sačuvan!")
        utils.emptyInput()
        return

    elif choice == "Izlaz":
        return

    console.clear()
    console.rule(choice)
    for station in presets[choice]:
        getArrivals(station)

    utils.emptyInput()


if __name__ == "__main__":
    console.clear()
    while 1 < 2:
        console.rule("NSmarter")
        choice = questionary.select(
            "Izaberite opciju:", choices=["Izbor stanica", "Izbor preseta", "Izlaz"]
        ).ask()

        if choice == "Izbor stanica":
            printStations()
            console.clear()

        elif choice == "Izbor preseta":
            printPresets()
            console.clear()

        elif choice == "Izlaz":
            console.clear()
            console.print("Hvala što ste koristili NSmarter!")
            exit()
