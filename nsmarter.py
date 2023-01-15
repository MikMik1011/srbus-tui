import os
import requests
import json
from datetime import date
import threading
from time import sleep
from collections import Counter

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


def saveConfig():
    with open(configPath, "w") as f:
        json.dump(config, f)


if not os.path.exists(dataDir):
    os.makedirs(dataDir)

if os.path.exists(stationsPath):
    with open(stationsPath) as f:
        stations = json.load(f)
else:
    stations = {}

allStations = None


def saveStations():
    with open(stationsPath, "w") as f:
        json.dump(stations, f)


if os.path.exists(presetsPath):
    with open(presetsPath) as f:
        presets = json.load(f)
else:
    presets = {}


def savePresets():
    with open(presetsPath, "w") as f:
        json.dump(presets, f)


if config["useStats"] and not config["useTermux"]:
    import matplotlib.pyplot as plt

    if os.path.exists(statsPath):
        with open(statsPath) as f:
            stats = json.load(f)
    else:
        stats = {}


def saveStats():
    with open(statsPath, "w") as f:
        json.dump(stats, f)


if not config["useTermux"]:
    from notifypy import Notify
else:
    from termux import Notification as tNotify


def sendNotification(text, nid=None):
    if not config["useTermux"]:
        notification = Notify()
        notification.title = "NSmarter"
        notification.message = text
        notification.send()

    else:
        tNotify.notify(
            title="NSmarter",
            content=text,
            nid=nid or text,
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


def notifyArrival(stId, busID, statDist):

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

    sendNotification(
        f"Autobus {busID} na liniji {lineNo} je udaljen {dist} stanica!",
        f"nsmarter-{lineNo}",
    )


def getArrivals(id, station=None):
    id = str(id)
    station = station or stations[id]
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

        saveStats()

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
                f"Unesite udaljenost stanica kada želite biti obavešteni (podrazumevano {config['stationsDistanceToNotify']}):"
            ).ask()
            if distToNotify:
                distToNotify = int(distToNotify)
            else:
                distToNotify = int(config["stationsDistanceToNotify"])

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


def searchStationByUUID(uuid):
    global allStations
    if not allStations:
        allStations = requests.get(
            config["allStationsEndpointURL"],
            headers={
                "X-Api-Authentication": config["apikey"],
                "User-Agent": "nsmarter",
            },
        ).json()

    for station in allStations["stations"]:
        if station["station_id"] == uuid:
            st = dict()

            st["name"] = station["name"]
            st["coords"] = station["coordinates"]
            st["sid"] = station["station_id"]

            return (station["id"], st)


def searchStationByName(name):
    global allStations

    if not allStations:
        allStations = requests.get(
            config["allStationsEndpointURL"],
            headers={
                "X-Api-Authentication": config["apikey"],
                "User-Agent": "nsmarter",
            },
        ).json()

    eligibleStations = {}

    for station in allStations["stations"]:
        if name.lower() in station["name"].lower():

            st = dict()
            st["name"] = station["name"]
            st["coords"] = station["coordinates"]
            st["sid"] = station["station_id"]

            eligibleStations[str(station["id"])] = st

    return eligibleStations


def findStation():
    method = questionary.select(
        "Kojom metodom želite pronaći stanicu?",
        choices=["Putem UUID-ja", "Putem imena stanice", "Izlaz"],
    ).ask()

    if method == "Putem UUID-ja":

        uuid = questionary.text("Unesite ID stanice:").ask()

        try:
            with console.status("Pretraga stanica u toku!"):
                id, station = searchStationByUUID(uuid)
        except TypeError:
            console.print("[bold red]Tražena stanica nije nađena!")
            utils.emptyInput()
            return

    else:

        name = questionary.text("Unesite ime (ili deo imena) stanice:").ask()
        with console.status("Pretraga stanica u toku!"):
            eligibleStations = searchStationByName(name)

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

    return (id, station)


def addStation():

    try:
        id, station = findStation()
    except TypeError:
        return

    if stations.get(str(id)):
        console.print("[bold red]Tražena stanica je već sačuvana!")
        utils.emptyInput()
        return
    stations[str(id)] = station

    saveStations()

    console.print(f"Stanica {station['name']} [green] je sačuvana!")
    utils.emptyInput()


def stationsMenu():
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
        addStation()
        return

    elif choice == "Izlaz":
        return

    id = list(stations.keys())[stList.index(choice)]

    action = questionary.select(
        "Šta želite da uradite?",
        choices=["Proveri dolaske", "Izbriši stanicu", "Izlaz"],
    ).ask()

    console.clear()

    if action == "Proveri dolaske":
        getArrivals(id)

    elif action == "Izbriši stanicu":
        del stations[id]
        saveStations()
        console.print(f"[bold green]Stanica {choice} uspešno obrisana!")

    else:
        return

    utils.emptyInput()


def presetsMenu():
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

        savePresets()

        console.print(f"Preset {name} [green]je sačuvan!")
        utils.emptyInput()
        return

    elif choice == "Izlaz":
        return

    action = questionary.select(
        "Šta želite da uradite?",
        choices=[
            "Proveri dolaske",
            "Izbriši preset",
            "Preimenjuj preset",
            "Promeni stanice u presetu",
            "Izlaz",
        ],
    ).ask()

    console.clear()
    if action == "Proveri dolaske":
        console.rule(choice)
        for station in presets[choice]:
            getArrivals(station)

    elif action == "Izbriši preset":
        del presets[choice]
        savePresets()
        console.print(f"[bold green]Preset {choice} uspešno obrisan!")

    elif action == "Preimenjuj preset":
        newName = questionary.text("Unesite novo ime preseta:").ask()
        presets[newName] = presets[choice]
        del presets[choice]
        savePresets()
        console.print(f"[bold green]Preset {choice} uspešno preimenovan u {newName}!")

    elif action == "Promeni stanice u presetu":
        options = []
        optStr = []
        for i in stations:
            text = f"{stations[str(i)]['name']} ({stations[str(i)]['sid']})"
            if i in presets[choice]:
                options.append(questionary.Choice(text, checked=True))
            else:
                options.append(text)

            optStr.append(text)

        stNames = questionary.checkbox("Izaberite stanice:", choices=options).ask()
        stIDs = [list(stations.keys())[optStr.index(i)] for i in stNames]
        presets[choice] = stIDs

        savePresets()

        console.print(f"Preset {choice} [green]je izmenjen!")
        utils.emptyInput()
        return

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
        stations[str(id)] = station
        saveStations()
        console.print(f"Stanica {station['name']} [green] je sačuvana!")

    utils.emptyInput()


def showStatsForStation(id, name):
    st = stats.get(id)
    if not st:
        console.print("[bold red]Nema podataka o ovoj stanici!")
        return

    plt.title("Broj pretraga stranice po danima")
    plt.suptitle(f"Stanica: {name}")
    plt.bar(list(st.keys()), list(st.values()))
    plt.xlabel("Datumi")
    plt.ylabel("Broj pretraga")
    with console.status("Otvaranje prozora sa grafikonom"):
        plt.show()


def statsMenu():
    console.clear()
    console.rule("Statistika")

    statType = questionary.select(
        "Izaberite tip statistike",
        choices=[
            "Broj pretraga stranice po danima",
            "Ukupan broj pretraga po danima",
        ],
    ).ask()

    if statType == "Broj pretraga stranice po danima":

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
        showStatsForStation(id, choice)

    elif statType == "Ukupan broj pretraga po danima":
        allDays = Counter()
        for station in stats:
            allDays += Counter(stats[station])
        allDays = dict(allDays)

        plt.title("Ukupan broj pretraga po danima")
        plt.bar(list(allDays.keys()), list(allDays.values()))
        plt.xlabel("Datumi")
        plt.ylabel("Broj pretraga")
        with console.status("Otvaranje prozora sa grafikonom"):
            plt.show()

    utils.emptyInput()


def settingsMenu():
    options = [
        {
            "name": f"Podrazumevana udaljenost stanica za notifikaciju: {config['stationsDistanceToNotify']}",
            "value": "stationsDistanceToNotify",
            "subMenuText": "Unesite novu podrazumevanu udaljenost stanica za notifikaciju:",
        },
        {"name": f"Upotreba statistike: {config['useStats']}", "value": "useStats"},
        {"name": f"Termux mod: {config['useTermux']}", "value": "useTermux"},
    ]

    if config["useTermux"]:
        options += [
            {
                "name": f"Boja LED lampice za notifikaciju (HEX RGB): {config['termuxNotifyLedClr']}",
                "value": "termuxNotifyLedClr",
                "subMenuText": "Unesite novu boju LED lampice u HEX RGB formatu:",
            },
            {
                "name": f"Patern vibracije za notifikacije: {config['termuxNotifyVibPattern']}",
                "value": "termuxNotifyVibPattern",
                "subMenuText": "Unesite novi patern vibracije. Svaku vibraciju odvojite zarezom. Vrednost vibracije je u milisekundama.",
            },
        ]

    options += [{"name": "Izlaz", "value": "Izlaz"}]
    action = questionary.select("Šta želite da izmenite?", choices=options).ask()

    if action == "Izlaz":
        return

    if type(config[action]) is not bool:
        newData = questionary.text(
            [i for i in options if i["value"] == action][0]["subMenuText"]
        ).ask()
        config[action] = newData
    else:
        newData = not config[action]

    config[action] = newData
    saveConfig()
    console.print(
        f'[bold green]Opcija {[i for i in options if i["value"] == action][0]["name"]} uspešno promenjena u {newData}!'
    )


if __name__ == "__main__":
    console.clear()

    while 1 < 2:

        choices = [
            "Izbor stanica",
            "Izbor preseta",
            "Brza provera stanice",
            "Podešavanja",
            "Izlaz",
        ]
        if config["useStats"] and not config["useTermux"]:
            choices.insert(3, "Pregled statistike")

        console.rule("NSmarter")

        choice = questionary.select("Izaberite opciju:", choices).ask()

        if choice == "Izbor stanica":
            stationsMenu()
            console.clear()

        elif choice == "Izbor preseta":
            presetsMenu()
            console.clear()

        elif choice == "Brza provera stanice":
            fastStationCheckMenu()
            console.clear()

        elif choice == "Pregled statistike":
            statsMenu()
            console.clear()

        elif choice == "Podešavanja":
            settingsMenu()
            console.clear()

        elif choice == "Izlaz":
            console.clear()
            console.print("Hvala što ste koristili NSmarter!")
            exit()
