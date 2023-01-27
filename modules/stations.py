import requests
from datetime import date
import threading
from time import sleep

from rich.table import Table
from rich import box
import questionary

from __main__ import console
from . import data, utils, fetch
from .i18n import getLocale as _


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
        _("notificationMsg").format(busID, lineNo, dist),
        f"nsmarter-{lineNo}",
    )


def getArrivals(id, station=None):
    id = str(id)
    station = station or data.stations[id]
    console.rule(_("stationHeader").format(station["name"], station["sid"]))

    try:
        with console.status(_("duringArrivalsCheck")):
            lines = fetch.checkStation(id)
    except requests.exceptions.ConnectionError:
        console.print(_("offline"))
        return

    if lines:
        table = Table(box=box.ROUNDED, show_lines=True)
        table.add_column(_("line"), justify="center")
        table.add_column(_("eta"), justify="center")
        table.add_column(_("stationsDistance"), justify="center")
        table.add_column(_("currentStation"), justify="center")
        table.add_column(_("busID"), justify="center")

        for arrival in lines:
            table.add_row(
                arrival["line"],
                utils.secondsToTimeString(arrival["eta"]),
                arrival["stationDiff"],
                arrival["lastStation"],
                arrival["busID"],
            )
        console.print(table)

        wantNotify = questionary.confirm(_("notificationPrompt")).ask()

        if wantNotify:
            choices = [
                _("stationsFar").format(i["line"], i["busID"], i["stationDiff"])
                for i in lines
            ]
            arrToCheck = questionary.checkbox(
                _("chooseArrivalsToTrack"), choices=choices
            ).ask()

            distToNotify = questionary.text(
                _("chooseDistanceToNotify").format(
                    data.config["stationsDistanceToNotify"]
                )
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
        console.print(_("noArrivals"))


def findStation():
    method = questionary.select(
        _("searchMethodPrompt"),
        choices=[_("searchUUID"), _("searchName"), _("exit")],
    ).ask()

    if method == _("searchUUID"):

        uuid = questionary.text(_("enterUUID")).ask()

        try:
            with console.status(_("stationsSearchStatus")):
                id, station = fetch.searchStationByUUID(utils.cirULat(uuid))
        except TypeError:
            console.print(_("stationNotFound"))
            utils.emptyInput()
            return

    elif method == _("searchName"):

        name = questionary.text(_("enterName")).ask()
        with console.status(_("stationsSearchStatus")):
            eligibleStations = fetch.searchStationByName(utils.cirULat(name))

        if not eligibleStations:
            console.print(_("stationNotFound"))
            utils.emptyInput()
            return

        stList = [
            f"{eligibleStations[str(i)]['name']} ({eligibleStations[str(i)]['sid']})"
            for i in eligibleStations
        ] + [
            _("exit"),
        ]

        choice = questionary.select(_("chooseStation"), choices=stList).ask()

        if choice == _("exit"):
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
        console.print(_("stationAlreadySaved"))
        utils.emptyInput()
        return
    data.stations[str(id)] = station

    data.saveStations()

    console.print(_("stationSavedSucc").format(station["name"]))
    utils.emptyInput()


def stationsMenu():
    console.clear()
    console.rule(_("stationJustHeader"))
    stList = [
        f"{data.stations[str(i)]['name']} ({data.stations[str(i)]['sid']})"
        for i in data.stations
    ] + [
        _("enterNewStation"),
        _("exit"),
    ]

    choice = questionary.select(_("chooseStation"), choices=stList).ask()

    if choice == _("enterNewStation"):
        addStation()
        return

    elif choice == _("exit"):
        return

    id = list(data.stations.keys())[stList.index(choice)]

    action = questionary.select(
        _("chooseAction"),
        choices=[_("checkArrivals"), _("deleteStation"), _("exit")],
    ).ask()

    console.clear()

    if action == _("checkArrivals"):
        getArrivals(id)

    elif action == _("deleteStation"):
        del data.stations[id]
        data.saveStations()
        console.print(_("stationDeletedSucc").format(choice))

    else:
        return

    utils.emptyInput()


def fastStationCheckMenu():
    try:
        id, station = findStation()
    except TypeError:
        return

    getArrivals(id, station)

    save = questionary.confirm(_("fastSavePrompt"), default=False).ask()

    if save:
        data.stations[str(id)] = station
        data.saveStations()
        console.print(_("stationSavedSucc").format(station["name"]))

    utils.emptyInput()
