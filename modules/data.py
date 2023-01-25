import os
import json

from __main__ import __file__

scriptDir = os.path.dirname(os.path.abspath(__file__))
configPath = os.path.join(scriptDir, "config.json")

dataDir = os.path.join(scriptDir, "data")
stationsPath = os.path.join(dataDir, "stations.json")
presetsPath = os.path.join(dataDir, "presets.json")
statsPath = os.path.join(dataDir, "stats.json")
localesDir = os.path.join(scriptDir, "locales")

with open(configPath, encoding="utf8") as f:
    config = json.load(f)


def saveConfig():
    with open(configPath, "w", encoding="utf8") as f:
        json.dump(config, f)


if not os.path.exists(dataDir):
    os.makedirs(dataDir)

if os.path.exists(stationsPath):
    with open(stationsPath, encoding="utf8") as f:
        stations = json.load(f)
else:
    stations = {}


def saveStations():
    with open(stationsPath, "w", encoding="utf8") as f:
        json.dump(stations, f)


if os.path.exists(presetsPath):
    with open(presetsPath, encoding="utf8") as f:
        presets = json.load(f)
else:
    presets = {}


def savePresets():
    with open(presetsPath, "w", encoding="utf8") as f:
        json.dump(presets, f)


if os.path.exists(statsPath):
    with open(statsPath, encoding="utf8") as f:
        stats = json.load(f)
else:
    stats = {}


def saveStats():
    with open(statsPath, "w", encoding="utf8") as f:
        json.dump(stats, f)

def getLocaleFileNames():
    return [i.replace(".json", "") for i in os.listdir(localesDir) if i.endswith(".json")]

def readLocaleFile(lang):
    fileName = f"{lang}.json"
    localePath = os.path.join(localesDir, fileName)

    assert os.path.exists(dataDir), f"{localePath} doesn't exist!"

    with open(localePath, encoding="utf8") as f:
        return json.load(f)
