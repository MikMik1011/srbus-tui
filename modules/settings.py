import questionary

from __main__ import console
from . import data, utils

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
    utils.emptyInput()
