from . import data

if not data.config["useTermux"]:
    from notifypy import Notify
else:
    from termux import Notification as tNotify

def sendNotification(text, nid=None):
    if not data.config["useTermux"]:
        notification = Notify()
        notification.title = "NSmarter"
        notification.message = text
        notification.send()

    else:
        tNotify.notify(
            title="NSmarter",
            content=text,
            nid=nid or text,
            kwargs={
                "group": "nsmarter",
                "led-color": data.config["termuxNotifyLedClr"],
                "vibrate": data.config["termuxNotifyVibPattern"],
                "priority": "max",
            },
        )


def secondsToTimeString(sec):
    return f"{sec // 60}:{sec % 60 :02}"


def emptyInput():
    input("\nPritisnite Enter da biste nastavili!")


def stationDifference(allStations, goalStation, currIndex):
    return abs(
        [str(i["id"]) for i in allStations].index(goalStation) + 1 - int(currIndex)
    )

cirULatUpper = str.maketrans("АБВГДЂЕЖЗИЈКЛМНОПРСТЋУФХЦЧШ", "ABVGDĐEŽZIJKLMNOPRSTĆUFHCČŠ")
cirULatLower = str.maketrans("абвгдђежзијклмнопрстћуфхцчш", "abvgdđežzijklmnoprstćufhcčš")
def cirULat(text):
    text = text.replace("љ", "lj").replace("Љ", "Lj")
    text = text.replace("њ", "nj").replace("Њ", "Nj")
    text = text.replace("Џ", "Dž").replace("џ", "dž")
    return text.translate(cirULatUpper).translate(cirULatLower)
