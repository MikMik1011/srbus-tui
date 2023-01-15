import questionary
from rich.console import Console

console = Console()

from modules import data, utils, stations, presets, stats, settings


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
            presets.presetsMenu()
            console.clear()

        elif choice == "Brza provera stanice":
            stations.fastStationCheckMenu()
            console.clear()

        elif choice == "Pregled statistike":
            stats.statsMenu()
            console.clear()

        elif choice == "Podešavanja":
            settings.settingsMenu()
            console.clear()

        elif choice == "Izlaz":
            console.clear()
            console.print("Hvala što ste koristili NSmarter!")
            exit()
