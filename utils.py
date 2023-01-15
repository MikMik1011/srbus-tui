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
