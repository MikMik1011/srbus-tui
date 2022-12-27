import requests
import json
import utils

configFile = open("./config.json")
config = json.load(configFile)
configFile.close()

for station in config["stations"]:
    print(f"\n\nStanica {station}: ")

    resp = requests.get(
        f"https://online.nsmart.rs/publicapi/v1/announcement/announcement.php?station_uid={station}",
        headers={"X-Api-Authentication": config["apikey"], "User-Agent": "nsmarter"},
    ).json()

    if (resp[0]['just_coordinates'] != "1"):

        for line in resp:
            print(f"\nLinija: {line['line_number']}")
            print(f"Procenjeno vreme do dolaska: {utils.secondsToTimeString(line['seconds_left'])}")
            print(f"Trenutna stanica autobusa: {line['vehicles'][0]['station_name']}")

    else:
        print("Nema dolazaka!")

