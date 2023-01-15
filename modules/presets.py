import questionary

from __main__ import console
from . import data, utils, stations
from .i18n import getLocale as _


def presetsMenu():
    console.clear()
    console.rule(_("presets"))

    prList = [i for i in data.presets.keys()] + [_("createNewPreset"), _("exit")]

    choice = questionary.select(_("choosePreset"), choices=prList).ask()

    if choice == _("createNewPreset"):
        name = questionary.text(_("presetNamePrompt")).ask()
        stList = [
            f"{data.stations[str(i)]['name']} ({data.stations[str(i)]['sid']})"
            for i in data.stations
        ]

        stNames = questionary.checkbox(_("chooseStation"), choices=stList).ask()
        stIDs = [list(data.stations.keys())[stList.index(i)] for i in stNames]
        data.presets[name] = stIDs

        data.savePresets()

        console.print(_("chooseStation").format(name))
        utils.emptyInput()
        return

    elif choice == _("exit"):
        return

    action = questionary.select(
        _("chooseAction"),
        choices=[
            _("checkArrivals"),
            _("deletePreset"),
            _("renamePreset"),
            _("editPreset"),
            _("exit"),
        ],
    ).ask()

    console.clear()
    if action == _("checkArrivals"):
        console.rule(choice)
        for station in data.presets[choice]:
            stations.getArrivals(station)

    elif action == _("deletePreset"):
        del data.presets[choice]
        data.savePresets()
        console.print(_("presetDeletedSucc").format(choice))

    elif action == _("renamePreset"):
        newName = questionary.text(_("presetNamePrompt")).ask()
        data.presets[newName] = data.presets[choice]
        del data.presets[choice]
        data.savePresets()
        console.print(_("presetRenamedSucc").format(choice, newName))

    elif action == _("editPreset"):
        options = []
        optStr = []
        for i in data.stations:
            text = f"{data.stations[str(i)]['name']} ({data.stations[str(i)]['sid']})"
            if i in data.presets[choice]:
                options.append(questionary.Choice(text, checked=True))
            else:
                options.append(text)

            optStr.append(text)

        stNames = questionary.checkbox(_("chooseStation"), choices=options).ask()
        stIDs = [list(data.stations.keys())[optStr.index(i)] for i in stNames]
        data.presets[choice] = stIDs

        data.savePresets()

        console.print(_("presetEditedSucc").format(choice))
        utils.emptyInput()
        return

    else:
        return

    utils.emptyInput()
