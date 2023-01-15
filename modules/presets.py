import questionary

from __main__ import console
from . import data, utils, stations


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
