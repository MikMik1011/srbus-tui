from . import data

locale = None
curLang = None


def updateLocale(lang):
    global locale, curLang
    locale = data.readLocaleFile(lang)
    curLang = lang


def getLocale(key):
    return locale[key] or f"Key {key} in {curLang} locale doesn't exist!"
