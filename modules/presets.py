import questionary

from __main__ import console
from . import data, utils, stations
from .i18n import getLocale as _


def presetsMenu():
    console.clear()
    console.rule(_("presets"))

    if not data.presets.get(data.config['city']):
        data.presets[data.config['city']] = {}
        
    prList = [i for i in data.presets[data.config['city']].keys()] + [_("createNewPreset"), _("exit")]

    choice = questionary.select(_("choosePreset"), choices=prList).ask()

    if choice == _("createNewPreset"):
        name = questionary.text(_("presetNamePrompt")).ask()
        stList = [
            f"{data.stations[data.config['city']][str(i)]['name']} ({data.stations[data.config['city']][str(i)]['sid']})"
            for i in data.stations[data.config['city']]
        ]

        stNames = questionary.checkbox(_("chooseStation"), choices=stList).ask()
        stIDs = [list(data.stations[data.config['city']].keys())[stList.index(i)] for i in stNames]
        data.presets[data.config['city']][name] = stIDs

        data.savePresets()

        console.print(_("presetSaved").format(name))
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
        
        if not data.presets.get(data.config['city']):
            data.presets[data.config['city']] = {}

        for station in data.presets[data.config['city']][choice]:
            stations.getArrivals(station)

    elif action == _("deletePreset"):
        del data.presets[data.config['city']][choice]
        data.savePresets()
        console.print(_("presetDeletedSucc").format(choice))

    elif action == _("renamePreset"):
        newName = questionary.text(_("presetNamePrompt")).ask()
        data.presets[data.config['city']][newName] = data.presets[data.config['city']][choice]
        del data.presets[data.config['city']][choice]
        data.savePresets()
        console.print(_("presetRenamedSucc").format(choice, newName))

    elif action == _("editPreset"):
        options = []
        optStr = []
        for i in data.stations[data.config['city']]:
            text = f"{data.stations[data.config['city']][str(i)]['name']} ({data.stations[data.config['city']][str(i)]['sid']})"

            if not data.presets.get(data.config['city']):
                data.presets[data.config['city']] = {}

            if i in data.presets[data.config['city']][choice]:
                options.append(questionary.Choice(text, checked=True))
            else:
                options.append(text)

            optStr.append(text)

        stNames = questionary.checkbox(_("chooseStation"), choices=options).ask()
        stIDs = [list(data.stations[data.config['city']].keys())[optStr.index(i)] for i in stNames]
        data.presets[data.config['city']][choice] = stIDs

        data.savePresets()

        console.print(_("presetEditedSucc").format(choice))
        utils.emptyInput()
        return

    else:
        return

    utils.emptyInput()
