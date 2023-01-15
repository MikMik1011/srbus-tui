from collections import Counter

import questionary
from rich.console import Console

console = Console()

from modules import data, utils, stations

if data.config["useStats"] and not data.config["useTermux"]:
    import matplotlib.pyplot as plt


def presetsMenu():
    console.clear()
    console.rule("Preseti")

    prList = [i for i in data.presets.keys()] + ["Napravi novi preset", "Izlaz"]

    choice = questionary.select("Izaberite preset:", choices=prList).ask()

    if choice == "Napravi novi preset":
        name = questionary.text("Unesite ime preseta: ").ask()
        stList = [
            f"{data.stations[str(i)]['name']} ({data.stations[str(i)]['sid']})" for i in data.stations
        ]

        stNames = questionary.checkbox("Izaberite stanice:", choices=stList).ask()
        stIDs = [list(data.stations.keys())[stList.index(i)] for i in stNames]
        data.presets[name] = stIDs

        data.savePresets()

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
        for station in data.presets[choice]:
            stations.getArrivals(station)

    elif action == "Izbriši preset":
        del data.presets[choice]
        data.savePresets()
        console.print(f"[bold green]Preset {choice} uspešno obrisan!")

    elif action == "Preimenjuj preset":
        newName = questionary.text("Unesite novo ime preseta:").ask()
        data.presets[newName] = data.presets[choice]
        del data.presets[choice]
        data.savePresets()
        console.print(f"[bold green]Preset {choice} uspešno preimenovan u {newName}!")

    elif action == "Promeni stanice u presetu":
        options = []
        optStr = []
        for i in data.stations:
            text = f"{data.stations[str(i)]['name']} ({data.stations[str(i)]['sid']})"
            if i in data.presets[choice]:
                options.append(questionary.Choice(text, checked=True))
            else:
                options.append(text)

            optStr.append(text)

        stNames = questionary.checkbox("Izaberite stanice:", choices=options).ask()
        stIDs = [list(data.stations.keys())[optStr.index(i)] for i in stNames]
        data.presets[choice] = stIDs

        data.savePresets()

        console.print(f"Preset {choice} [green]je izmenjen!")
        utils.emptyInput()
        return

    else:
        return

    utils.emptyInput()


def fastStationCheckMenu():
    try:
        id, station = stations.findStation()
    except TypeError:
        return

    stations.getArrivals(id, station)

    save = questionary.confirm(
        "Da li ipak želite da sačuvate stanicu?", default=False
    ).ask()

    if save:
        data.stations[str(id)] = station
        data.saveStations()
        console.print(f"Stanica {station['name']} [green] je sačuvana!")

    utils.emptyInput()


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

    utils.emptyInput()


def settingsMenu():
    options = [
        {
            "name": f"Podrazumevana udaljenost stanica za notifikaciju: {data.config['stationsDistanceToNotify']}",
            "value": "stationsDistanceToNotify",
            "subMenuText": "Unesite novu podrazumevanu udaljenost stanica za notifikaciju:",
        },
        {"name": f"Upotreba statistike: {data.config['useStats']}", "value": "useStats"},
        {"name": f"Termux mod: {data.config['useTermux']}", "value": "useTermux"},
    ]

    if data.config["useTermux"]:
        options += [
            {
                "name": f"Boja LED lampice za notifikaciju (HEX RGB): {data.config['termuxNotifyLedClr']}",
                "value": "termuxNotifyLedClr",
                "subMenuText": "Unesite novu boju LED lampice u HEX RGB formatu:",
            },
            {
                "name": f"Patern vibracije za notifikacije: {data.config['termuxNotifyVibPattern']}",
                "value": "termuxNotifyVibPattern",
                "subMenuText": "Unesite novi patern vibracije. Svaku vibraciju odvojite zarezom. Vrednost vibracije je u milisekundama.",
            },
        ]

    options += [{"name": "Izlaz", "value": "Izlaz"}]
    action = questionary.select("Šta želite da izmenite?", choices=options).ask()

    if action == "Izlaz":
        return

    if type(data.config[action]) is not bool:
        newData = questionary.text(
            [i for i in options if i["value"] == action][0]["subMenuText"]
        ).ask()
        data.config[action] = newData
    else:
        newData = not data.config[action]

    data.config[action] = newData
    data.saveConfig()
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
        if data.config["useStats"] and not data.config["useTermux"]:
            choices.insert(3, "Pregled statistike")

        console.rule("NSmarter")

        choice = questionary.select("Izaberite opciju:", choices).ask()

        if choice == "Izbor stanica":
            stations.stationsMenu()
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
