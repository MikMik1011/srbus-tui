from collections import Counter
import questionary

from __main__ import console
from . import data, utils
from .i18n import getLocale as _

if not data.config["useTermux"]:
    import matplotlib.pyplot as plt


def showStatsForStation(id):
    st = data.stats.get(id)
    if not st:
        console.print(_("noStationStats"))
        return

    plt.title(_("stationSearchesDaily"))
    plt.bar(list(st.keys()), list(st.values()))
    plt.xlabel(_("dates"))
    plt.ylabel(_("numberOfSearches"))
    with console.status(_("openPlt")):
        plt.show()

def showStatsTotal():
    allDays = Counter()

    for station in data.stats:
        allDays += Counter(data.stats[station])
    allDays = dict(allDays)

    plt.title(_("totalSearchesDaily"))
    plt.bar(list(allDays.keys()), list(allDays.values()))
    plt.xlabel(_("dates"))
    plt.ylabel(_("numberOfSearches"))

    with console.status(_("openPlt")):
        plt.show()

matPlotImported = False

def statsMenu():


    console.clear()
    console.rule(_("stats"))

    statType = questionary.select(
        _("chooseStatsType"),
        choices=[
            _("stationSearchesDaily"),
            _("totalSearchesDaily"),
            _("exit")
        ],
    ).ask()

    if statType == _("stationSearchesDaily"):

        stList = [
            f"{data.stations[str(i)]['name']} ({data.stations[str(i)]['sid']})" for i in data.stations
        ] + [
            _("exit"),
        ]

        choice = questionary.select(_("chooseStation"), choices=stList).ask()

        if choice == _("exit"):
            return

        id = str(list(data.stations.keys())[stList.index(choice)])
        console.clear()
        showStatsForStation(id)

    elif statType == _("totalSearchesDaily"):
        showStatsTotal()

    else:
        return

    utils.emptyInput()
