try:
    from pip._internal.main import main as pipmain
except ModuleNotFoundError:
    from pip import main as pipmain

import os

scriptDir = os.path.dirname(os.path.abspath(__file__))
reqsDir = os.path.join(scriptDir, "requirements")


def setTermuxConfig():
    print("Uključivanje Termux moda...")

    import json

    configPath = os.path.join(scriptDir, "config.json")

    with open(configPath, "r", encoding="utf8") as f:
        config = json.load(f)

    config["useTermux"] = True

    with open(configPath, "w", encoding="utf8") as f:
        json.dump(config, f)

    print("Termux mod uključen!")


def install_modules(termux=False):
    if termux:
        setTermuxConfig()
        reqPath = os.path.join(reqsDir, "requirements-termux.txt")

    else:
        reqPath = os.path.join(reqsDir, "requirements.txt")

    pipmain(["install", "-r", reqPath])


print("0) Instalacija na PC-ju")
print("1) Instalacija na Termuxu")

choice = -1

while choice != 0 and choice != 1:
    try:
        choice = int(input("Izbor: "))
    except ValueError:
        pass

install_modules(termux=bool(choice))
