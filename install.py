try:
    from pip._internal.main import main as pipmain
except ModuleNotFoundError:
    from pip import main as pipmain

def setTermuxConfig():
    print("Uključivanje Termux moda...")

    import json
    import os
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    configPath = os.path.join(scriptDir, "config.json")

    with open(configPath, "r", encoding="utf8") as f:
        config = json.load(f)

    config["useTermux"] = True

    with open(configPath, "w", encoding="utf8") as f:
        json.dump(config, f)

    print("Termux mod uključen!")


def install_modules(termux=False):
    if termux:
        pipmain(['install', '-r', 'requirements-termux.txt'])
        setTermuxConfig()

        return

    pipmain(['install', '-r', 'requirements.txt'])

print("0) Instalacija na PC-ju")
print("1) Instalacija na Termuxu")
choice = -1
while choice != 0 and choice != 1:
    try:
        choice = int(input("Izbor: "))
    except TypeError:
        pass

install_modules(termux=bool(choice))
