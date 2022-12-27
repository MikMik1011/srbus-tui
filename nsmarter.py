import requests
import json

configFile = open("./config.json")
config = json.load(configFile)
configFile.close()

for station in config["stations"]:
    print(f"\nStanica {station}: ")

    resp = requests.get(
        f"https://online.nsmart.rs/publicapi/v1/announcement/announcement.php?station_uid={station}",
        headers={"X-Api-Authentication": config["apikey"], "User-Agent": "nsmarter"},
    ).json()

    if (resp[0]['just_coordinates'] != "1"):

        for line in resp:
            secLeft = line['seconds_left']
            print(f"Linija: {line['line_number']}\tMinuti do dolaska: {secLeft // 60}:{secLeft % 60 :02}")

    else:
        print("Nema dolazaka!")

