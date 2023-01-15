from collections import Counter
import questionary

from __main__ import console
from . import data, utils

def showStatsForStation(id, name):
    st = data.stats.get(id)
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

def showStatsTotal():
    allDays = Counter()

    for station in data.stats:
        allDays += Counter(data.stats[station])
    allDays = dict(allDays)

    plt.title("Ukupan broj pretraga po danima")
    plt.bar(list(allDays.keys()), list(allDays.values()))
    plt.xlabel("Datumi")
    plt.ylabel("Broj pretraga")

    with console.status("Otvaranje prozora sa grafikonom"):
        plt.show()

matPlotImported = False

def statsMenu():

    global matPlotImported
    if not matPlotImported:
        with console.status("Učitavanje [italic]matplotlib [not italic]biblioteke"):
            import matplotlib.pyplot as plt
            matPlotImported = True

    console.clear()
    console.rule("Statistika")

    statType = questionary.select(
        "Izaberite tip statistike",
        choices=[
            "Broj pretraga stranice po danima",
            "Ukupan broj pretraga po danima",
            "Izlaz"
        ],
    ).ask()

    if statType == "Broj pretraga stranice po danima":

        stList = [
            f"{data.stations[str(i)]['name']} ({data.stations[str(i)]['sid']})" for i in data.stations
        ] + [
            "Izlaz",
        ]

        choice = questionary.select("Izaberite stanicu:", choices=stList).ask()

        if choice == "Izlaz":
            return

        id = str(list(data.stations.keys())[stList.index(choice)])
        console.clear()
        showStatsForStation(id, choice)

    elif statType == "Ukupan broj pretraga po danima":
        showStatsTotal()

    else:
        return

    utils.emptyInput()
