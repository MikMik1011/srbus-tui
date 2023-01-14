import os
import requests
import json
from datetime import date
import threading
from time import sleep

import questionary
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

import utils


scriptDir = os.path.dirname(os.path.abspath(__file__))
configPath = os.path.join(scriptDir, "config.json")
dataDir = os.path.join(scriptDir, "data")
stationsPath = os.path.join(dataDir, "stations.json")
presetsPath = os.path.join(dataDir, "presets.json")
statsPath = os.path.join(dataDir, "stats.json")

with open(configPath) as f:
    config = json.load(f)

if not os.path.exists(dataDir):
    os.makedirs(dataDir)

if os.path.exists(stationsPath):
    with open(stationsPath) as f:
        stations = json.load(f)
else:
    stations = {}

if os.path.exists(presetsPath):
    with open(presetsPath) as f:
        presets = json.load(f)
else:
    presets = {}

if config["useStats"] and not config["useTermux"]:
    import matplotlib.pyplot as plt

    if os.path.exists(statsPath):
        with open(statsPath) as f:
            stats = json.load(f)
    else:
        stats = {}

if not config["useTermux"]:
    from notifypy import Notify
else:
    from termux import Notification as tNotify


def sendNotification(text):
    if not config["useTermux"]:
        notification = Notify()
        notification.title = "NSmarter"
        notification.message = text
        notification.send()

    else:
        tNotify.notify(
            title="NSmarter",
            content=text,
            nid=text,
            kwargs={
                "group": "nsmarter",
                "led-color": config["termuxNotifyLedClr"],
                "vibrate": config["termuxNotifyVibPattern"],
                "priority": "max",
            },
        )


def checkStation(id):
    arrivals = []

    resp = requests.get(
        f"{config['stationEndpointURL']}{id}",
        headers={"X-Api-Authentication": config["apikey"], "User-Agent": "nsmarter"},
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


def notifyArrival(stId, busID, statDist=config["stationsDistanceToNotify"]):

    statDist = int(statDist)
    dist = None
    lineNo = None

    while dist == None or dist > statDist:

        try:
            lines = checkStation(stId)
        except requests.exceptions.ConnectionError:
            return

        if lines:

            found = False
            for arrival in lines:
                if arrival["busID"] == busID:
                    found = True
                    dist = int(arrival["stationDiff"])
                    if not lineNo:
                        lineNo = arrival["line"]
                    break

            if not found:
                dist = 0

            sleep(10)

    sendNotification(f"Autobus {busID} na liniji {lineNo} je udaljen {dist} stanica!")


def getArrivals(id):
    id = str(id)
    station = stations[id]
    console.rule(f"Stanica {station['name']} ({station['sid']}):")

    try:
        with console.status("Provera dolazaka je u toku!"):
            lines = checkStation(id)
    except requests.exceptions.ConnectionError:
        console.print("Proverite internet konekciju!")
        return

    if config["useStats"] and not config["useTermux"]:

        if not stats.get(id):
            stats[id] = {}

        today = date.today().strftime("%Y-%m-%d")

        if not stats[id].get(today):
            stats[id][today] = 0

        stats[id][today] += 1

        with open(statsPath, "w") as f:
            json.dump(stats, f)

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

        wantNotify = questionary.confirm(
            "Da li zelite da dobijete notifikaciju kad se određeni autobus približi?"
        ).ask()

        if wantNotify:
            choices = [
                f"[{i['line']}] ({i['busID']}) {i['stationDiff']} stanica daleko"
                for i in lines
            ]
            arrToCheck = questionary.checkbox(
                "Izaberite dolaske koje želite da pratite", choices=choices
            ).ask()

            for arrival in arrToCheck:
                busID = lines[choices.index(arrival)]["busID"]
                threading.Thread(
                    target=notifyArrival,
                    args=(id, busID),
                    name=f"nsmarter-notify:{busID}",
                    daemon=True,
                ).start()

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

    with open(stationsPath, "w") as f:
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

        with open(presetsPath, "w") as f:
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


def showStats(id):
    st = stats.get(id)
    if not st:
        console.print("[bold red]Nema podataka o ovoj stanici!")
        return

    plt.bar(list(st.keys()), list(st.values()))
    plt.xlabel("Datumi")
    plt.ylabel("Broj pretraga")
    with console.status("Otvaranje prozora sa grafikonom"):
        plt.show()


def seeStats():
    console.clear()
    console.rule("Statistika")
    stList = [
        f"{stations[str(i)]['name']} ({stations[str(i)]['sid']})" for i in stations
    ] + [
        "Izlaz",
    ]

    choice = questionary.select("Izaberite stanicu:", choices=stList).ask()

    if choice == "Izlaz":
        return

    id = str(list(stations.keys())[stList.index(choice)])
    console.clear()
    showStats(id)

    utils.emptyInput()


if __name__ == "__main__":
    console.clear()
    choices = ["Izbor stanica", "Izbor preseta", "Izlaz"]
    if config["useStats"] and not config["useTermux"]:
        choices.insert(2, "Pregled statistike")

    while 1 < 2:
        console.rule("NSmarter")

        choice = questionary.select("Izaberite opciju:", choices).ask()

        if choice == "Izbor stanica":
            printStations()
            console.clear()

        elif choice == "Izbor preseta":
            printPresets()
            console.clear()

        elif choice == "Pregled statistike":
            seeStats()
            console.clear()

        elif choice == "Izlaz":
            console.clear()
            console.print("Hvala što ste koristili NSmarter!")
            exit()
