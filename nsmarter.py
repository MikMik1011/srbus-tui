import questionary
from rich.console import Console

console = Console()

from modules import data, utils, stations, presets, stats, settings, i18n

_ = i18n.getLocale

if __name__ == "__main__":
    console.clear()

    i18n.updateLocale(data.config["locale"])

    while 1 < 2:

        choices = [
            _("chooseStation"),
            _("choosePreset"),
            _("quickStationCheck"),
            _("settings"),
            _("exit"),
        ]
        if data.config["useStats"] and not data.config["useTermux"]:
            choices.insert(3, _("checkStats"))

        console.rule("NSmarter")

        choice = questionary.select(_("chooseOption"), choices).ask()

        if choice == _("chooseStation"):
            stations.stationsMenu()

        elif choice == _("choosePreset"):
            presets.presetsMenu()

        elif choice == _("quickStationCheck"):
            stations.fastStationCheckMenu()

        elif choice == _("checkStats"):
            stats.statsMenu()

        elif choice == _("settings"):
            settings.settingsMenu()

        elif choice == _("exit"):
            console.clear()
            console.print(_("exitMsg"))
            exit()

        console.clear()
