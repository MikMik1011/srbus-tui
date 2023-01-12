def secondsToTimeString(sec):
    return f"{sec // 60}:{sec % 60 :02}"


def emptyInput():
    input("\nPritisnite Enter da biste nastavili!")


def stationDifference(allStations, goalStation, currIndex):
    return abs(
        [str(i["id"]) for i in allStations].index(goalStation) + 1 - int(currIndex)
    )
