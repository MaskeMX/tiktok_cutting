#!/usr/bin/env bash
# Lädt eine per Link freigegebene Google-Drive-Datei in Originalgröße herunter.
# Nutzung: bash setup/drive_fetch.sh <FILE_ID> <ziel.mov>
# FILE_IDs findet Claude über den Google-Drive-Connector (search_files, parentId = Ordner-ID).
set -e
curl -sSL -m 900 -o "$2" "https://drive.usercontent.google.com/download?id=$1&export=download&confirm=t"
if file "$2" | grep -q HTML; then echo "FEHLER: Datei nicht per Link freigegeben (HTML statt Video)"; rm -f "$2"; exit 1; fi
ls -la "$2"
