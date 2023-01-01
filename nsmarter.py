import requests
import json
import utils

with open("./config.json") as f:
    config = json.load(f)
try:
    with open("./data/stations.json") as f:
        stations = json.load(f)
except:
    stations = {}


def checkStation(id):
    arrivals = []

    resp = requests.get(
            f"{config['stationEndpointURL']}{id}",
            headers={"X-Api-Authentication": config["apikey"], "User-Agent": "nsmarter"},
    ).json()

    if (resp[0]['just_coordinates'] != "1"):

        for arr in resp:
            arrivals.append({
                "line": arr['line_number'],
                "eta": arr['seconds_left'],
                "lastStation": arr['vehicles'][0]['station_name']
            })
    return arrivals

def getArrivals():
    for id, station in stations.items():
        print(f"\n\nStanica {station['name']}: ")

        try:
            lines = checkStation(id)
        except requests.exceptions.ConnectionError:
            print("Proverite internet konekciju!")
            return

        if lines:
            for arrival in lines:
                print(f"\nLinija: {arrival['line']}")
                print(f"Procenjeno vreme do dolaska: {utils.secondsToTimeString(arrival['eta'])}")
                print(f"Trenutna stanica autobusa: {arrival['lastStation']}")
        else:
            print("Nema dolazaka!")

def searchStation(uuid):
    resp = requests.get(
            config['allStationsEndpointURL'],
            headers={"X-Api-Authentication": config["apikey"], "User-Agent": "nsmarter"},
    ).json()

    for station in resp['stations']:
        if station['station_id'] == uuid:
            st = dict()

            st['name'] = station['name']
            st['coords'] = station['coordinates']
            st['sid'] = station['station_id']

            return (station['id'], st)

def addStation():
    uuid = input("Unesite ID stanice: ")
    id, station = searchStation(uuid)

    if id:
        if stations.get(str(id)):
            print("Tražena stanica je već sačuvana!")
            return

        stations[id] = station
        with open("./data/stations.json", "w") as f:
            json.dump(stations, f)
        
        print(f"Stanica {station['name']} je dodata!")
    else:
        print("Tražena stanica nije nađena!")


if __name__ == "__main__":
    print("Dobrodošli u NSmarter!")
    
    while 1 < 2:
        print("\nUnesite 1 za proveru dolazaka autobusa.")
        print("Unesite 2 za dodavanje nove stanice.")

        choice = input("Izbor: ")

        if choice == "1":
            getArrivals()
        if choice == "2":
            addStation()
