import requests
import json
import utils

with open("./config.json") as f:
    config = json.load(f)


def checkStation(id):
    arrivals = []

    resp = requests.get(
            f"https://online.nsmart.rs/publicapi/v1/announcement/announcement.php?station_uid={id}",
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
    for station in config["stations"]:
        print(f"\n\nStanica {station}: ")

        try:
            lines = checkStation(station)
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
            f"https://online.nsmart.rs/publicapi/v1/networkextended.php?action=get_cities_extended",
            headers={"X-Api-Authentication": config["apikey"], "User-Agent": "nsmarter"},
    ).json()

    for station in resp['stations']:
        if station['station_id'] == uuid:
            return station['id']

def addStation():
    uuid = input("Unesite ID stanice: ")
    sid = searchStation(uuid)

    if sid:
        config["stations"].append(sid)
        
        with open("./config.json", "w") as f:
            json.dump(config, f)
        
        print("Stanica je dodata!")
    else:
        print("Trazena stanica nije nadjena!")


if __name__ == "__main__":
    print("Dobrodosli u NSmarter!")
    
    while 1 < 2:
        print("\nUnesite 1 za proveru dolazaka autobusa.")
        print("Unesite 2 za dodavanje nove stanice.")

        choice = input("Izbor: ")

        if choice == "1":
            getArrivals()
        if choice == "2":
            addStation()
