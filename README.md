# SrBus

## Napomena: ovaj projekat je arhiviran, naslednik ovog projekta je [bgpp](https://github.com/MikMik1011/bgpp), frontend + backend web aplikacija.

### Open-source CLI klijent za proveru dolazaka autobusa u Srbiji (Beograd, Novi Sad, Niš).

## Features

- Suckless, bez raznih gluposti koje čine zvanične aplikacije sporima
- Dobijanje informacija o liniji, procenjenom vremenu, broj stanica za koliko je autobus udaljen, ime trenutne stanice i ID autobusa u preglednoj tabeli
- Čuvanje omiljenih stanica jednim klikom
- Mogućnost dodavanja stanica preko ID-ja ili imena stanice
- Preseti, tj. grupisanje stanica, tako da možete proveriti dolaske za više stanica istovremeno
- Slanje notifikacija kada autobus bude na određenom broju stanica od željene stanice
- Termux integracija pomoću Termux:API
- Lokalizacija


## Instalacija i pokretanje

- `git clone https://github.com/MikMik1011/srbus`
- `cd srbus`
- `python install.py`
- Unesite 0 ili 1, u zavisnosti da li skidate skriptu na računar ili Termux
- `python srbus.py`

## Credits
- <a href="https://github.com/FmasterofU">FmasterofU</a>, za njegovo <a href="https://github.com/FmasterofU/NSmart-RE"> reverse enginnerovanje NSmart API-ja </a> 
- Moje nervne ćelije i ostali organi, za preživljavanje suočavanja sa najgorim API-jem koji postoji na ovoj kugli zemaljskoj. Ovi iz BusLogica bolje da su zaposlili novorođenčad da im radi, pa i oni bi bolje napravili taj API.
