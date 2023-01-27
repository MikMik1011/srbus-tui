import questionary

from __main__ import console
from . import data, utils, i18n

from .i18n import getLocale as _


def settingsMenu():
    options = [
        {
            "name": _("language-name").format(data.config["locale"]),
            "value": "locale",
        },
        {
            "name": _("stationsDistanceToNotify-name").format(
                data.config["stationsDistanceToNotify"]
            ),
            "value": "stationsDistanceToNotify",
            "subMenuText": _("stationsDistanceToNotify-subMenuText"),
        },
        {
            "name": _("useTermux-name").format(data.config["useTermux"]),
            "value": "useTermux",
        },
    ]

    if data.config["useTermux"]:
        options += [
            {
                "name": "Boja LED lampice za notifikaciju (HEX RGB): {0}".format(
                    data.config["termuxNotifyLedClr"]
                ),
                "value": "termuxNotifyLedClr",
                "subMenuText": _("termuxNotifyLedClr-subMenuText"),
            },
            {
                "name": _("termuxNotifyVibPattern-name").format(
                    data.config["termuxNotifyVibPattern"]
                ),
                "value": "termuxNotifyVibPattern",
                "subMenuText": _("termuxNotifyVibPattern-subMenuText"),
            },
        ]

    options += [{"name": _("exit"), "value": _("exit")}]
    action = questionary.select(_("chooseAction"), choices=options).ask()

    if action == _("exit"):
        return

    elif action == "locale":
        lang = questionary.select(
            _("language-subMenuText"), choices=data.getLocaleFileNames()
        ).ask()

        i18n.updateLocale(lang)
        data.config["locale"] = lang
        data.saveConfig()

        console.print(_("langChangedSucc").format(lang))
        utils.emptyInput()

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
        _("settingChangedSucc").format(
            [i for i in options if i["value"] == action][0]["name"], newData
        )
    )
    utils.emptyInput()
