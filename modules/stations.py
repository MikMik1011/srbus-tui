import requests
from datetime import date
import threading
from time import sleep

from rich.table import Table
from rich import box
import questionary

from . import data, utils, fetch
from __main__ import console

def notifyArrival(stId, busID, statDist):

    statDist = int(statDist)
    dist = None
    lineNo = None

    while dist == None or dist > statDist:

        try:
            lines = fetch.checkStation(stId)
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

    utils.sendNotification(
        f"Autobus {busID} na liniji {lineNo} je udaljen {dist} stanica!",
        f"nsmarter-{lineNo}",
    )


def getArrivals(id, station=None):
    id = str(id)
    station = station or data.stations[id]
    console.rule(f"Stanica {station['name']} ({station['sid']}):")

    try:
        with console.status("Provera dolazaka je u toku!"):
            lines = fetch.checkStation(id)
    except requests.exceptions.ConnectionError:
        console.print("Proverite internet konekciju!")
        return

    if data.config["useStats"] and not data.config["useTermux"]:

        if not data.stats.get(id):
            data.stats[id] = {}

        today = date.today().strftime("%Y-%m-%d")

        if not data.stats[id].get(today):
            data.stats[id][today] = 0

        data.stats[id][today] += 1

        data.saveStats()

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

            distToNotify = questionary.text(
                f"Unesite udaljenost stanica kada želite biti obavešteni (podrazumevano {data.config['stationsDistanceToNotify']}):"
            ).ask()
            if distToNotify:
                distToNotify = int(distToNotify)
            else:
                distToNotify = int(data.config["stationsDistanceToNotify"])

            for arrival in arrToCheck:
                busID = lines[choices.index(arrival)]["busID"]
                threading.Thread(
                    target=notifyArrival,
                    args=(id, busID, distToNotify),
                    name=f"nsmarter-notify:{busID}",
                    daemon=True,
                ).start()

    else:
        console.print("Nema dolazaka!")



def findStation():
    method = questionary.select(
        "Kojom metodom želite pronaći stanicu?",
        choices=["Putem UUID-ja", "Putem imena stanice", "Izlaz"],
    ).ask()

    if method == "Putem UUID-ja":

        uuid = questionary.text("Unesite ID stanice:").ask()

        try:
            with console.status("Pretraga stanica u toku!"):
                id, station = fetch.searchStationByUUID(utils.cirULat(uuid))
        except TypeError:
            console.print("[bold red]Tražena stanica nije nađena!")
            utils.emptyInput()
            return

    elif method == "Putem imena stanice":

        name = questionary.text("Unesite ime (ili deo imena) stanice:").ask()
        with console.status("Pretraga stanica u toku!"):
            eligibleStations = fetch.searchStationByName(utils.cirULat(name))

        if not eligibleStations:
            console.print("[bold red]Tražena stanica nije nađena!")
            utils.emptyInput()
            return

        stList = [
            f"{eligibleStations[str(i)]['name']} ({eligibleStations[str(i)]['sid']})"
            for i in eligibleStations
        ] + [
            "Izlaz",
        ]

        choice = questionary.select("Izaberite stanicu:", choices=stList).ask()

        if choice == "Izlaz":
            console.clear()
            return

        id = list(eligibleStations.keys())[stList.index(choice)]
        station = eligibleStations[id]

    else:
        return
        
    return (id, station)


def addStation():

    try:
        id, station = findStation()
    except TypeError:
        return

    if data.stations.get(str(id)):
        console.print("[bold red]Tražena stanica je već sačuvana!")
        utils.emptyInput()
        return
    data.stations[str(id)] = station

    data.saveStations()

    console.print(f"Stanica {station['name']} [green] je sačuvana!")
    utils.emptyInput()


def stationsMenu():
    console.clear()
    console.rule("Stanice")
    stList = [
        f"{data.stations[str(i)]['name']} ({data.stations[str(i)]['sid']})" for i in data.stations
    ] + [
        "Unos nove stanice",
        "Izlaz",
    ]

    choice = questionary.select("Izaberite stanicu:", choices=stList).ask()

    if choice == "Unos nove stanice":
        addStation()
        return

    elif choice == "Izlaz":
        return

    id = list(data.stations.keys())[stList.index(choice)]

    action = questionary.select(
        "Šta želite da uradite?",
        choices=["Proveri dolaske", "Izbriši stanicu", "Izlaz"],
    ).ask()

    console.clear()

    if action == "Proveri dolaske":
        getArrivals(id)

    elif action == "Izbriši stanicu":
        del data.stations[id]
        data.saveStations()
        console.print(f"[bold green]Stanica {choice} uspešno obrisana!")

    else:
        return

    utils.emptyInput()

def fastStationCheckMenu():
    try:
        id, station = findStation()
    except TypeError:
        return

    getArrivals(id, station)

    save = questionary.confirm(
        "Da li ipak želite da sačuvate stanicu?", default=False
    ).ask()

    if save:
        data.stations[str(id)] = station
        data.saveStations()
        console.print(f"Stanica {station['name']} [green] je sačuvana!")

    utils.emptyInput()